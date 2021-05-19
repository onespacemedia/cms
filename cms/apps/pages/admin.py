'''
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
'''
import collections
import json
from copy import deepcopy
from functools import cmp_to_key, partial

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_permission_codename
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models, transaction
from django.db.models import F, Max, Q
from django.forms import modelform_factory
from django.http import (Http404, HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden, HttpResponseRedirect)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import capfirst
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html

from cms.admin import PageBaseAdmin
from cms.apps.pages.models import (Country, CountryGroup, Page,
                                   PageSearchAdapter, get_registered_content)

# Used to track references to and from the JS sitemap.
from cms.apps.pages.utils import duplicate_page, publish_page

PAGE_FROM_KEY = 'from'
PAGE_FROM_SITEMAP_VALUE = 'sitemap'

# The GET parameter used to indicate content type on page creation.
PAGE_TYPE_PARAMETER = 'type'
VERSIONING_ENABLED = getattr(settings, 'PAGES_VERSIONING', False)


class PageOverviewChangeList(ChangeList):
    def url_for_result(self, result):
        return reverse('admin:pages_page_overview', kwargs={'object_id': result.id})


class PageContentTypeFilter(admin.SimpleListFilter):
    '''Enables filtering of pages by their content type.'''
    title = 'page type'

    parameter_name = 'page_type'

    def lookups(self, request, model_admin):
        lookups = []
        content_types = ContentType.objects.get_for_models(*get_registered_content())
        for key, value in content_types.items():
            lookups.append((value.id, capfirst(key._meta.verbose_name)))
        lookups.sort(key=lambda item: item[1])
        return lookups

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type_id=int(self.value()))
        return queryset


class PageAdmin(PageBaseAdmin):
    '''Admin settings for Page models.'''

    list_display = ('__str__', 'last_modified', 'content_type', 'is_online',)

    list_editable = ('is_online',)

    list_filter = [PageContentTypeFilter]

    shared_fields = ['slug', 'parent', 'publication_date', 'expiry_date', 'is_online', 'requires_authentication']
    version_readonly = ['slug', 'parent']
    version_fields = ['version_publication_date']
    version_exclude = ['publication_date', 'expiry_date', 'is_online', 'requires_authentication']

    PUBLICATION_FIELDS = ('Publication', {
        'fields': ['publication_date', 'expiry_date', 'is_online'],
        'classes': ('collapse',)
    })

    GENERAL_FIELDS = (None, {
        'fields': ['title', 'slug', 'parent'],
    })

    if VERSIONING_ENABLED:
        GENERAL_FIELDS[1]['fields'].append('version_name')
        PUBLICATION_FIELDS[1]['fields'].append('version_publication_date')

    new_fieldsets = [
        GENERAL_FIELDS,
        ('Security', {
            'fields': ('requires_authentication',),
        }),
        PUBLICATION_FIELDS,
        ('Navigation', {
            'fields': ('short_title', 'in_navigation', 'hide_from_anonymous'),
            'classes': ('collapse',)
        })
    ]

    new_fieldsets.extend(PageBaseAdmin.fieldsets)

    removed_fieldsets = [
        new_fieldsets.index(PageBaseAdmin.TITLE_FIELDS),
        new_fieldsets.index(PageBaseAdmin.PUBLICATION_FIELDS),
        new_fieldsets.index(PageBaseAdmin.NAVIGATION_FIELDS)
    ]

    fieldsets = []

    for k, v in enumerate(new_fieldsets):
        if k not in removed_fieldsets:
            fieldsets.append(v)

    search_adapter_cls = PageSearchAdapter

    change_form_template = 'admin/pages/page/change_form.html'

    def get_changelist(self, request, **kwargs):
        if VERSIONING_ENABLED:
            return PageOverviewChangeList
        return ChangeList

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_canonical_page=True)

    def get_object(self, request, object_id, from_field=None):
        queryset = super().get_queryset(request)
        model = queryset.model
        field = model._meta.pk if from_field is None else model._meta.get_field(
            from_field)
        try:
            object_id = field.to_python(object_id)
            return queryset.get(**{field.name: object_id})
        except (model.DoesNotExist, ValidationError, ValueError):
            return None

    def _register_page_inline(self, model):
        '''Registers the given page inline with reversion.'''
        self._reversion_autoregister(model, follow=['page'])

    def __init__(self, *args, **kwargs):
        '''Initialzies the PageAdmin.'''
        super().__init__(*args, **kwargs)
        # Patch the admin class's index template.
        self.admin_site.index_template = 'admin/pages/dashboard.html'
        # Prepare to register some content inlines.
        self.content_inlines = []
        # Register all page inlines.
        for content_cls in get_registered_content():
            self._register_page_inline(content_cls)

    def register_content_inline(self, content_cls, inline_admin):
        '''Registers an inline model with the page admin.'''
        self.content_inlines.append((content_cls, inline_admin))
        self._register_page_inline(inline_admin.model)

    def get_inline_instances(self, request, obj=None):
        '''Returns all the inline instances for this PageAdmin.'''
        try:
            inline_instances = super().get_inline_instances(request, obj)
        except TypeError:
            inline_instances = super().get_inline_instances(request)
        # Add on the relevant content inlines.
        obj = getattr(request, '_admin_change_obj', None)  # HACK: Retrieve the page from the change view.
        content_cls = self.get_page_content_cls(request, obj)
        for cls, inline in self.content_inlines:
            if cls == content_cls:
                inline_instances.append(inline(self.model, self.admin_site))
        # All done!
        return inline_instances

    # Reversion
    def get_revision_instances(self, request, obj):
        '''Returns all the instances to be used in this object's revision.'''
        instances = [obj]
        # Add the content object.
        instances.append(obj.content)
        # Add all the content inlines.
        for _, inline in self.content_inlines:
            # pass
            try:
                instances.extend(inline.model._default_manager.filter(page=obj))
            except:
                pass
        return instances

    @staticmethod
    def get_revision_form_data(request, obj, version):
        '''
        Returns a dictionary of data to set in the admin form in order to revert
        to the given revision.
        '''
        data = version.field_dict
        content_version = version.revision.version_set.all().get(
            content_type=obj.content_type_id,
            object_id=obj.pk,
        )
        data.update(content_version.field_dict)
        return data

    # Plugable content types.
    @staticmethod
    def get_page_content_cls(request, obj=None):
        '''Retrieves the page content type slug.'''
        if obj and not hasattr(request, '_admin_change_obj'):
            request._admin_change_obj = obj

        if PAGE_TYPE_PARAMETER in request.GET:
            return ContentType.objects.get_for_id(request.GET[PAGE_TYPE_PARAMETER]).model_class()

        if obj and hasattr(obj, 'content_type') and obj.content_type:
            return obj.content_type.model_class()

        if hasattr(request, '_admin_change_obj') and hasattr(request._admin_change_obj, 'content_type'):
            return request._admin_change_obj.content_type.model_class()

        raise Http404('You must specify a page content type.')

    def get_shared_fields(self, request, obj=None):
        return self.shared_fields or []

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj) or [])
        if not getattr(request, 'shared_fields_editable', False):
            fields += self.version_readonly

        return fields

    def get_prepopulated_fields(self, request, obj=None):
        fields = super().get_prepopulated_fields(request, obj)
        if fields:
            fields = fields.copy()
        for f in self.get_readonly_fields(request, obj):
            fields.pop(f, None)
        return fields

    def get_fieldsets(self, request, obj=None):
        '''Generates the custom content fieldsets.'''
        content_cls = self.get_page_content_cls(request, obj)
        content_fields = [
            field.name for field in content_cls._meta.fields + content_cls._meta.many_to_many
            if field.name != 'page'
        ]

        fieldsets = deepcopy(super().get_fieldsets(request, obj))
        exclude = []
        if obj and obj.version_for_id:
            exclude += self.version_exclude
        else:
            exclude += self.version_fields

        for fieldset in fieldsets:
            fieldset[1]['fields'] = [field for field in fieldset[1]['fields'] if field not in exclude]

        fieldsets = [fieldset for fieldset in fieldsets if fieldset[1]['fields']]

        if content_fields:
            content_fieldsets = content_cls.fieldsets or [
                ('Page content', {
                    'fields': content_fields,
                }),
            ]
            fieldsets = list(fieldsets[0:1]) + content_fieldsets + list(fieldsets[1:])
        return fieldsets

    def get_all_children(self, page):
        '''Returns all the children for a page.'''
        children = []

        def do_get_all_children(page):
            for child in page.children:
                children.append(child)
                do_get_all_children(child)
        do_get_all_children(page)
        return children

    def get_breadcrumbs(self, page):
        '''Returns all breadcrumbs for a page.'''
        breadcrumbs = []
        while page:
            breadcrumbs.append(page)
            page = page.parent
        breadcrumbs.reverse()
        return breadcrumbs

    def get_form(self, request, obj=None, **kwargs):
        '''Adds the template area fields to the form.'''
        if not getattr(settings, 'PAGES_VERSIONING', False):
            request.shared_fields_editable = True

        content_cls = self.get_page_content_cls(request, obj)
        content_fields = []
        form_attrs = {}
        for field in content_cls._meta.fields + content_cls._meta.many_to_many:
            if field.name == 'page':
                continue
            form_field = self.formfield_for_dbfield(field, request=request)
            # HACK: add in the initial value. No other way to pass this on.
            if obj:
                try:
                    form_field.initial = getattr(obj.content, field.name, '')
                    if isinstance(field, models.ManyToManyField) and not form_field.initial == '':
                        form_field.initial = form_field.initial.all()
                except content_cls.DoesNotExist:
                    # This means that we're in a reversion recovery, or
                    # something weird has happened to the database.
                    pass

            if field.name in getattr(content_cls, 'filter_horizontal', ()):
                form_field.widget = FilteredSelectMultiple(
                    field.verbose_name,
                    is_stacked=False,
                )
            # Store the field.
            form_attrs[field.name] = form_field
            content_fields.append(field.name)
        ContentForm = type('{}Form'.format(self.__class__.__name__), (forms.ModelForm,), form_attrs)
        defaults = {'form': ContentForm}
        defaults.update(kwargs)

        content_defaults = {
            'form': ContentForm,
            'fields': content_fields,
            "formfield_callback": partial(self.formfield_for_dbfield, request=request)
        }

        class PageForm(super().get_form(request, obj, **defaults)):
            content_form_cls = modelform_factory(content_cls, **content_defaults)

            def full_clean(self):
                super().full_clean()
                content_instance = None
                if self.instance.content_type_id:
                    content_instance = self.instance.content
                content_form = self.content_form_cls(self.data or None, instance=content_instance)
                self._errors.update(content_form.errors)

        # HACK: Need to limit parents field based on object. This should be
        # done in formfield_for_foreignkey, but that method does not know
        # about the object instance.
        if obj:
            invalid_parents = set(child.id for child in self.get_all_children(obj))
            invalid_parents.add(obj.id)
        else:
            invalid_parents = frozenset()
        homepage = request.pages.homepage

        if homepage:
            parent_choices = []
            for page in [homepage] + self.get_all_children(homepage):
                if page.id not in invalid_parents:
                    parent_choices.append((page.id, ' \u203a '.join('{}'.format(breadcrumb.title) for breadcrumb in self.get_breadcrumbs(page))))
        else:
            parent_choices = []

        if not parent_choices:
            parent_choices = (('', '---------'),)

        if 'parent' in PageForm.base_fields:
            if obj and not (not obj._is_canonical_page or obj.owner_set.exists() or obj.version_set.exists()):
                PageForm.base_fields['parent'].choices = parent_choices
            elif not obj:
                PageForm.base_fields['parent'].choices = parent_choices

        # Return the completed form.
        return PageForm

    def save_model(self, request, obj, form, change):
        '''Saves the model and adds its content fields.'''
        content_cls = self.get_page_content_cls(request, obj)
        content_cls_type = ContentType.objects.get_for_model(content_cls)
        # Delete the old page content, if it's expired.
        if change and ContentType.objects.get_for_id(obj.content_type_id) != content_cls_type:
            obj.content.delete()
        # Create the page content.
        obj.content_type = content_cls_type
        if change:
            try:
                content_obj = content_cls_type.model_class().objects.get(page=obj)
            except content_cls.DoesNotExist:
                content_obj = content_cls()  # This means that we're in a reversion recovery, or something weird has happened to the database.
        else:
            content_obj = content_cls()
        # Modify the page content.
        for field in content_obj._meta.fields:
            if field.name == 'page':
                continue
            # This will not necessarily be in the form; if you change something
            # that is `list_editable` in the changelist, for example.
            if field.name in form.cleaned_data:
                setattr(content_obj, field.name, form.cleaned_data[field.name])

        # Save the model.
        super().save_model(request, obj, form, change)
        # Save the page content.
        content_obj.page = obj
        content_obj.save()

        # Now save m2m fields.
        for field in content_obj._meta.many_to_many:
            getattr(content_obj, field.name).set(form.cleaned_data[field.name])

        obj.content = content_obj

    # Permissions.
    @staticmethod
    def has_add_content_permission(request, model):
        '''Checks whether the given user can edit the given content model.'''
        opts = model._meta
        return request.user.has_perm('{0}.{1}'.format(opts.app_label, get_permission_codename('add', opts)))

    def has_add_permission(self, request):
        '''Checks whether the user can edits pages and at least one content model.'''
        if not super().has_add_permission(request):
            return False
        for content_model in get_registered_content():
            if self.has_add_content_permission(request, content_model):
                return True
        return False

    def has_change_permission(self, request, obj=None):
        '''Checks whether the user can edit the page and associated content model.'''
        if not super().has_change_permission(request, obj):
            return False
        if obj:
            content_model = ContentType.objects.get_for_id(obj.content_type_id).model_class()
            content_opts = content_model._meta
            return request.user.has_perm('{0}.{1}'.format(
                content_opts.app_label,
                get_permission_codename('change', content_opts)
            ))
        return True

    def has_delete_permission(self, request, obj=None):
        '''Checks whether the user can delete the page and associated content model.'''
        if not super().has_delete_permission(request, obj):
            return False
        if obj:
            content_model = ContentType.objects.get_for_id(obj.content_type_id).model_class()
            content_opts = content_model._meta
            return request.user.has_perm('{0}.{1}'.format(
                content_opts.app_label,
                get_permission_codename('delete', content_opts)
            ))
        return True

    # Custom views.
    def patch_response_location(self, request, response):
        '''Perpetuates the 'from' key in all redirect responses.'''
        if isinstance(response, HttpResponseRedirect):
            if PAGE_FROM_KEY in request.GET:
                response['Location'] += '?%s=%s' % (PAGE_FROM_KEY, request.GET[PAGE_FROM_KEY])
        return response

    def changelist_view(self, request, extra_context=None):
        '''Redirects to the sitemap, if appropriate.'''
        if PAGE_FROM_KEY in request.GET:
            redirect_slug = request.GET[PAGE_FROM_KEY]
            if redirect_slug == PAGE_FROM_SITEMAP_VALUE:
                return redirect('admin:index')
        return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        '''Uses only the correct inlines for the page.'''
        # HACK: Add the current page to the request to pass to the get_inline_instances() method.
        current_page = get_object_or_404(self.model, id=object_id)

        request._admin_change_obj = current_page

        page = current_page

        page_versioning = getattr(settings, 'PAGES_VERSIONING', False)
        page_languages = 'cms.middleware.LocalisationMiddleware' in settings.MIDDLEWARE

        extra_context = extra_context or {}
        extra_context['display_version_options'] = page_versioning
        extra_context['display_language_options'] = page_languages

        if page_versioning:
            if current_page.version_for:
                version = current_page
                # The 'live' page
                page = version.version_for
            extra_context['live_page'] = page
            extra_context['page_versions'] = page.get_versions()

        if page_languages:
            extra_context['language_pages'] = page.get_language_pages()

        # page could be a language version
        extra_context['canonical_version'] = page.canonical_version

        # Call the change view.
        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def revision_view(self, request, object_id, version_id, extra_context=None):
        '''Load up the correct content inlines.'''
        # HACK: Add the current page to the request to pass to the get_inline_instances() method.
        page = get_object_or_404(self.model, id=object_id)
        request._admin_change_obj = page
        # Call the change view.
        return super().revision_view(request, object_id, version_id, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        '''Ensures that a valid content type is chosen.'''
        request.shared_fields_editable = True
        if PAGE_TYPE_PARAMETER not in request.GET:
            # Generate the available content items.
            content_items = get_registered_content()

            def cmp_function(a, b):
                return (a.classifier > b.classifier) - (a.classifier < b.classifier) or \
                       (a._meta.verbose_name.lower() > b._meta.verbose_name.lower()) - (a._meta.verbose_name.lower() < b._meta.verbose_name.lower())

            content_items.sort(key=cmp_to_key(cmp_function))
            content_types = []
            for content_type in content_items:
                if self.has_add_content_permission(request, content_type):
                    # If we get this far, then we have permisison to add a page of this type.
                    get_params = request.GET.copy()
                    get_params[PAGE_TYPE_PARAMETER] = ContentType.objects.get_for_model(content_type).id
                    query_string = get_params.urlencode()
                    content_url = request.path + '?' + query_string
                    content_type_context = {
                        'name': content_type._meta.verbose_name,
                        'icon': staticfiles_storage.url(content_type.icon),
                        'url': content_url,
                        'classifier': content_type.classifier
                    }
                    content_types.append(content_type_context)
            # Shortcut for when there is a single content type.
            if len(content_types) == 1:
                return redirect(content_types[0]['url'])
            # Render the select page template.
            context = {
                'title': 'Select page type',
                'content_types': content_types,
                'is_popup': request.GET.get(IS_POPUP_VAR, False),
            }

            return render(request, 'admin/pages/page/select_page_type.html', context)
        else:
            if not self.has_add_content_permission(request, ContentType.objects.get_for_id(request.GET[PAGE_TYPE_PARAMETER]).model_class()):
                raise PermissionDenied('You are not allowed to add pages of that content type.')
        return super().add_view(request, form_url, extra_context)

    def get_preserved_filters(self, request):
        '''
            This is to fix an always present issue in our CMS where if there were preserved filters from the list view,
            the type of page being saved would not be passed to the form action of the change form. This mean that on
            posting, the admin would think the user was on the page type selection page and not trying to save the form.
            We just need to add the PAGE_TYPE_PARAMETER to the form action if there are preserved filters.

            For more info see: https://github.com/onespacemedia/osm-jet/issues/11
        '''
        preserved_filters = super().get_preserved_filters(request)

        if preserved_filters and request.GET.get(PAGE_TYPE_PARAMETER):
            preserved_filters = f'{preserved_filters}&{PAGE_TYPE_PARAMETER}={request.GET.get(PAGE_TYPE_PARAMETER)}'

        return preserved_filters

    def response_add(self, request, obj, post_url_continue=None):
        '''Redirects to the sitemap if appropriate.'''
        response = super().response_add(request, obj, post_url_continue)
        return self.patch_response_location(request, response)

    def response_change(self, request, obj):
        '''Redirects to the sitemap if appropriate.'''
        response = super().response_change(request, obj)
        return self.patch_response_location(request, response)

    def delete_view(self, request, object_id, extra_context=None):
        '''Redirects to the sitemap if appropriate.'''
        response = super().delete_view(request, object_id, extra_context)
        return self.patch_response_location(request, response)

    def get_urls(self):
        '''Adds in some custom admin URLs.'''
        admin_view = self.admin_site.admin_view

        from django.urls import path

        return [
            path('sitemap.json', admin_view(self.sitemap_json_view), name='pages_page_sitemap_json'),
            path('move-page/', admin_view(self.move_page_view), name='pages_page_move_page'),
            path('<path:object_id>/overview/', admin_view(self.page_index), name='pages_page_overview'),
            path('<path:object_id>/publish/', admin_view(self.publish_version), name='pages_page_publishversion'),
            path('<path:object_id>/duplicate/', admin_view(self.duplicate_for_country_group), name='pages_page_duplicate'),
            path('<path:object_id>/new-version/', admin_view(self.duplicate_for_version), name='pages_page_addversion'),
        ] + super().get_urls()

    def page_index(self, request, object_id, form_url='', extra_context=None):
        request.shared_fields_editable = True
        page = get_object_or_404(self.model, id=object_id)

        # This view doesn't make sense for page versions
        if page.version_for_id:
            raise Http404('There\'s no page overview for versions of pages')

        fields = self.get_shared_fields(request, page)

        ModelForm = super().get_form(request, page, fields=fields, change=True)
        fieldsets = [
            ('Shared Fields', {
                'fields': self.get_shared_fields(request, page)
            })
        ]

        context = extra_context or {}

        def filter_available_fields(fields_, available):
            if isinstance(fields_, collections.Mapping):
                field_dict = fields_.copy()
                for key, value in fields_.items():
                    if key not in available or not all([x in available for x in value]):
                        field_dict.pop(key)
                return field_dict
            return [field for field in fields_ if field in available]

        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=page)
            if form.is_valid():
                context['form_saved'] = True
                form.save()
                updated_fields = {
                    field: getattr(page, field) for field in fields
                }
                page.get_versions().update(**updated_fields)
        else:
            form = ModelForm(instance=page)

        admin_form = helpers.AdminForm(
            form,
            list(fieldsets),
            # Clear prepopulated fields on a view-only form to avoid a crash.
            filter_available_fields(self.get_prepopulated_fields(request, page), fields),
            filter_available_fields(self.get_readonly_fields(request, page), fields),
            model_admin=self,
        )
        media = self.media + admin_form.media

        page_languages = 'cms.middleware.LocalisationMiddleware' in settings.MIDDLEWARE

        context['display_language_options'] = page_languages

        if page_languages:
            context['language_pages'] = page.get_language_pages()

        errors = helpers.AdminErrorList(form, [])

        has_file_field = form.is_multipart()

        context.update({
            **self.admin_site.each_context(request),
            'is_popup': False,
            'page_versions': page.get_versions(),
            'original': page,
            'canonical_version': page.canonical_version,
            'adminform': admin_form,
            'errors': errors,
            'has_view_permission': self.has_view_permission(request, page),
            'has_add_permission': self.has_add_permission,
            'has_change_permission': self.has_change_permission(request, page),
            'has_delete_permission': self.has_delete_permission(request, page),
            'has_editable_inline_admin_formsets': False,
            'show_add': False,
            'show_return': False,
            'has_file_field': has_file_field,
            'save_as_new': False,
            'change': True,
            'save_as_version': False,
            'opts': page._meta,
            'media': media
        })

        return TemplateResponse(request, 'admin/pages/page/versions_list.html', context)

    @transaction.atomic
    def publish_version(self, request, object_id, **kwargs):
        page = get_object_or_404(self.model, id=object_id)
        live_page = publish_page(page)
        if not live_page:
            return HttpResponseBadRequest('<p>This page is already published!</p>')

        msg_dict = {
            'obj': live_page.get_version_name()
        }
        msg = '"{obj}" published successfully'
        self.message_user(request, format_html(msg, **msg_dict), messages.SUCCESS)

        return redirect(live_page.get_admin_url())

    def sitemap_json_view(self, request):
        '''Returns a JSON data structure describing the sitemap.'''
        # Get the homepage.
        homepage = request.pages.homepage
        # Compile the initial data.
        data = {
            'canAdd': self.has_add_permission(request),
            'createHomepageUrl': reverse('admin:pages_page_add') + '?{0}={1}'.format(PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
            'moveUrl': reverse('admin:pages_page_move_page') or None,
            'addUrl': reverse('admin:pages_page_add') + '?{0}={1}&parent=__id__'.format(PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
            'changeUrl': reverse('admin:pages_page_change', args=('__id__',)) + '?{0}={1}'.format(PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
            'deleteUrl': reverse('admin:pages_page_delete', args=('__id__',)) + '?{0}={1}'.format(PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
        }
        # Add in the page data.
        if homepage:
            def sitemap_entry(page):
                children = []
                for child in page.children:
                    children.append(sitemap_entry(child))
                return {
                    'isOnline': page.is_online,
                    'id': page.id,
                    'title': str(page),
                    'children': children,
                    'canChange': self.has_change_permission(request, page),
                    'canDelete': self.has_delete_permission(request, page),
                }
            data['entries'] = [sitemap_entry(homepage)]
        else:
            data['entries'] = []
        # Render the JSON.
        response = HttpResponse(content_type='application/json; charset=utf-8')
        json.dump(data, response)
        return response

    @transaction.atomic
    def move_page_view(self, request):
        '''Moves a page up or down.'''
        # Check that the user has permission to move pages.
        if not self.has_change_permission(request):
            return HttpResponseForbidden('You do not have permission to move this page.')

        # Lock entire table.
        existing_pages_list = Page.objects.all().exclude(
            is_canonical_page=False,
        ).select_for_update().values(
            'id',
            'parent_id',
            'left',
            'right',
            'title'
        ).order_by('left')
        existing_pages = dict(
            (page['id'], page)
            for page
            in existing_pages_list
        )

        # Get the page.
        page = existing_pages[int(request.POST['page'])]
        parent_id = page['parent_id']

        # Get all the siblings.
        siblings = [s for s in existing_pages_list if s['parent_id'] == parent_id]

        # Find the page to swap.
        direction = request.POST['direction']

        if direction == 'up':
            siblings.reverse()
        elif direction == 'down':
            pass
        else:
            raise ValueError('Direction should be "up" or "down".')

        sibling_iter = iter(siblings)
        for sibling in sibling_iter:
            if sibling['id'] == page['id']:
                break
        try:
            other_page = next(sibling_iter)
        except StopIteration:
            return HttpResponse('Page could not be moved, as nothing to swap with.')

        # Put the pages in order.
        first_page, second_page = sorted((page, other_page), key=lambda p: p['left'])

        # Excise the first page.
        Page.objects.filter(left__gte=first_page['left'], right__lte=first_page['right']).update(
            left=F('left') * -1,
            right=F('right') * -1,
        )

        # Move the other page.
        branch_width = first_page['right'] - first_page['left'] + 1
        Page.objects.filter(left__gte=second_page['left'], right__lte=second_page['right']).update(
            left=F('left') - branch_width,
            right=F('right') - branch_width,
        )

        # Put the page back in.
        second_branch_width = second_page['right'] - second_page['left'] + 1
        Page.objects.filter(left__lte=-first_page['left'], right__gte=-first_page['right']).update(
            left=(F('left') - second_branch_width) * -1,
            right=(F('right') - second_branch_width) * -1,
        )

        # Update all content models to match the left and right of their parents.
        existing_pages_list = Page.objects.all().exclude(
            is_canonical_page=True,
        ).select_for_update().values(
            'id',
            'parent_id',
            'owner',
            'left',
            'right',
            'title'
        ).order_by('left')

        for child_page in existing_pages_list:
            child_page.update(
                left=F('owner__left'),
                right=F('owner__right'),
            )

        # Report back.
        return HttpResponse('Page #%s was moved %s.' % (page['id'], direction))

    @transaction.atomic
    def duplicate_for_country_group(self, request, object_id, *args, **kwargs):
        def page_changes(new_page, original_page):
            new_page.is_online = False
            new_page.owner = original_page
            new_page.country_group = CountryGroup.objects.get(pk=request.POST.get('country_group'))
            new_page.left = None
            new_page.right = None

            return new_page

        # Get the current page
        original_page = get_object_or_404(Page, id=object_id)

        # Catch if a language duplicate is made from a translation page
        if original_page.owner:
            original_page = original_page.owner

        if request.method == 'POST':
            page = duplicate_page(original_page, page_changes)

            return redirect('/admin/pages/page/{}'.format(page.pk))

        country_groups = CountryGroup.objects.all()

        if not country_groups:
            messages.add_message(request, messages.ERROR, 'You need to add at least one country group first before you can add a copy of this page')
            return redirect('/admin/pages/page/{}'.format(original_page.pk))

        context = dict(
            original_page=original_page,
            country_groups=country_groups
        )

        return TemplateResponse(request, 'admin/pages/page/language_duplicate.html', context)

    @transaction.atomic
    def duplicate_for_version(self, request, object_id, *args, **kwargs):
        def page_changes(new_page, original_page):
            parent_page = original_page.version_for or original_page
            new_page.version_for = parent_page

            highest_version = parent_page.version_set.aggregate(Max('version'))['version__max'] or parent_page.version

            new_page.version = highest_version + 1

            new_page.left = None
            new_page.right = None

            return new_page

        page = get_object_or_404(self.model, id=object_id)

        if request.method == 'POST':
            page = duplicate_page(page, page_changes)
            return redirect(reverse('admin:pages_page_change', kwargs={'object_id': page.id}))

        context = dict(
            original_page=page,
        )

        return TemplateResponse(request, 'admin/pages/page/version_duplicate.html', context)

    def get_view_on_site_parameters(self, obj=None):
        params = super().get_view_on_site_parameters(obj)
        if obj.version_for_id or obj.version_set.exists():
            params['version'] = obj.version
        return params


class CountryGroupAdmin(admin.ModelAdmin):
    pass


class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'group')


admin.site.register(Page, PageAdmin)

if 'cms.middleware.LocalisationMiddleware' in settings.MIDDLEWARE:
    admin.site.register(Country, CountryAdmin)
    admin.site.register(CountryGroup, CountryGroupAdmin)

page_admin = admin.site._registry[Page]
