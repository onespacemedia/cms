"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""

from __future__ import unicode_literals, with_statement

from copy import deepcopy
from functools import update_wrapper
from random import randint

from django.contrib import admin, messages
from django.contrib.auth import get_permission_codename
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.text import capfirst
from mptt.admin import MPTTModelAdmin
from suit.admin import SortableModelAdmin

from cms import externals
from cms.apps.pages.models import (Page, PageSearchAdapter,
                                   get_registered_content, DEFAULT_LANGUAGES)

from .forms import generate_page_form

# Used to track references to and from the JS sitemap.
PAGE_FROM_KEY = "from"
PAGE_FROM_SITEMAP_VALUE = "sitemap"


# The GET parameter used to indicate content type.
PAGE_TYPE_PARAMETER = "type"


class SortableMPTTModelAdmin(MPTTModelAdmin, SortableModelAdmin):

    def __init__(self, *args, **kwargs):
        super(SortableMPTTModelAdmin, self).__init__(*args, **kwargs)
        mptt_opts = self.model._mptt_meta
        # NOTE: use mptt default ordering
        self.ordering = (mptt_opts.tree_id_attr, mptt_opts.left_attr)
        if self.list_display and self.sortable not in self.list_display:
            self.list_display = list(self.list_display) + [self.sortable]

        self.list_editable = self.list_editable or []
        if self.sortable not in self.list_editable:
            self.list_editable = list(self.list_editable) + [self.sortable]

        self.exclude = self.exclude or []
        if self.sortable not in self.exclude:
            self.exclude = list(self.exclude) + [self.sortable]

    # NOTE: return default admin ChangeList
    def get_changelist(self, request, **kwargs):
        return admin.views.main.ChangeList


class PageAdmin(SortableMPTTModelAdmin):

    list_display = ['__str__', 'languages']
    list_display_links = ['__str__']

    mptt_indent_field = '__str__'
    mptt_level_indent = 20

    sortable = 'order'

    search_adapter_cls = PageSearchAdapter

    def get_urls(self):
        from django.conf.urls import url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = [
            url(r'^$', wrap(self.changelist_view), name='%s_%s_changelist' % info),
            url(r'^add/$', wrap(self.add_view), name='%s_%s_add' % info),
            url(r'^duplicate/$', wrap(self.duplicate_view), name='%s_%s_duplicate' % info),
            url(r'^(.+)/history/$', wrap(self.history_view), name='%s_%s_history' % info),
            url(r'^(.+)/delete/$', wrap(self.delete_view), name='%s_%s_delete' % info),
            url(r'^(.+)/$', wrap(self.change_view), name='%s_%s_change' % info),
        ]
        return urlpatterns

    def _register_page_inline(self, model):
        """Registeres the given page inline with reversion."""
        if externals.reversion:
            self._autoregister(model, follow=["page"])
            adapter = self.revision_manager.get_adapter(Page)
            try:
                adapter.follow = tuple(adapter.follow) + (model._meta.get_field("page").related.get_accessor_name(),)
                adapter.follow = tuple(name for name in adapter.follow if name != '+')
            except:
                pass

    def __init__(self, *args, **kwargs):
        """Initialzies the PageAdmin."""
        super(PageAdmin, self).__init__(*args, **kwargs)
        # Prepare to register some content inlines.
        self.content_inlines = []
        # Register all page inlines.
        for content_cls in get_registered_content():
            self._register_page_inline(content_cls)

        if externals.reversion:
            self.list_display.insert(1, "last_modified")

    # Reversion

    def get_revision_instances(self, request, object):
        """Returns all the instances to be used in this object's revision."""
        instances = super(PageAdmin, self).get_revision_instances(request, object)
        # Add the content object.
        instances.append(object.content)
        # Add all the content inlines.
        for _, inline in self.content_inlines:
            # pass
            try:
                instances.extend(inline.model._default_manager.filter(page=object))
            except:
                pass
        return instances

    def get_revision_form_data(self, request, obj, version):
        """
        Returns a dictionary of data to set in the admin form in order to revert
        to the given revision.
        """
        data = super(PageAdmin, self).get_revision_form_data(request, obj, version)
        content_version = version.revision.version_set.all().get(
            content_type=obj.content_type_id,
            object_id_int=obj.pk,
        )
        data.update(content_version.field_dict)
        return data

    # Plugable content types.
    def get_breadcrumbs(self, page):
        """Returns all breadcrumbs for a page."""
        breadcrumbs = []
        while page:
            breadcrumbs.append(page)
            page = page.parent
        breadcrumbs.reverse()
        return breadcrumbs

    def get_form(self, request, obj=None, **kwargs):
        """Adds the template area fields to the form."""
        if obj is None:
            content_items = get_registered_content()

            kwargs['form'] = generate_page_form(invalid_parents=[
                page.pk for page in Page.objects.root_nodes()
            ], content_types=[
                (ContentType.objects.get_for_model(content_type).id, capfirst(content_type._meta.verbose_name))
                for content_type in content_items
                if self.has_add_content_permission(request, content_type)
            ])

        return super(PageAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            if 'page' in request.GET:
                obj.pk = request.GET['page']
            else:
                obj.order = 0
                obj.save()

            content_type = ContentType.objects.get_for_id(form.cleaned_data['page_type']).model_class()
            content_type.objects.create(
                page=obj,
                title=form.cleaned_data['title'],
                slug=form.cleaned_data['slug'],
                language=form.cleaned_data['language'],
            )
        else:
            obj.save()

        # Invalidate page cache
        tree_cache_keys = [
            'page_tree_{}'.format(language[0])
            for language in DEFAULT_LANGUAGES
            ]
        nav_cache_keys = [
            'page_nav_{}'.format(language[0])
            for language in DEFAULT_LANGUAGES
            ]
        for key in tree_cache_keys:
            cache.delete(key)
        for key in nav_cache_keys:
            cache.delete(key)

        page_content_cache_keys = [
            'page_{}_{}_content'.format(obj.pk, language[0])
            for language in DEFAULT_LANGUAGES
            ]
        for key in page_content_cache_keys:
            cache.delete(key)

        cache.delete('page_{}_content'.format(
            obj.pk
        ))

        cache.delete('page_{}_children'.format(
            obj.pk
        ))

    # Permissions.
    def has_add_content_permission(self, request, model):
        """Checks whether the given user can edit the given content model."""
        opts = model._meta
        return request.user.has_perm("{0}.{1}".format(opts.app_label, get_permission_codename('add', opts)))

    # Custom views.
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}

        # Get the content objects which are tied to this page.
        extra_context['content_objects'] = []

        for model in get_registered_content():
            objects = model.objects.filter(
                page_id=object_id,
            )

            extra_context['content_objects'].extend(objects)

        return super(PageAdmin, self).changeform_view(request, object_id, form_url, extra_context)

    def get_fieldsets(self, request, obj=None):

        if obj is None:
            fieldsets = [
                (None, {
                    'fields': ['title', 'slug', 'parent', 'language', 'page_type']
                })
            ]

            if 'page' in request.GET:
                del fieldsets[0][1]['fields'][2]

            self.prepopulated_fields = {'slug': ('title',)}

        else:
            fieldsets = [
                (None, {
                    'fields': ['parent']
                })
            ]

            self.prepopulated_fields = {}

        return fieldsets

    def duplicate_view(self, request, *args, **kwargs):

        # Get the page we are going to duplicate
        page = get_object_or_404(Page, pk=request.GET.get('page', None))

        # Create list to store content objects in
        content_objects = []

        # Loop the registered content models
        for model in get_registered_content():

            # Extend the content objects list attached to the current page
            content_objects.extend(model.objects.filter(
                page_id=page.pk,
            ))

        # If the user has come from the post request and its a yes...
        if request.method == 'POST' and request.POST.get('post', 'no') == 'yes':

            # Duplicate the page
            new_page = deepcopy(page)
            new_page.pk = None # Strip pk to save as a valid copy
            new_page.save()

            # Loop the content objects...
            for content_object in content_objects:

                # Duplicate the content object
                new_content_object = deepcopy(content_object)
                new_content_object.pk = None # Strip pk to save as a valid copy
                new_content_unique_key = randint(10000, 99999)
                new_content_object.title = "{} - {}".format(
                    new_content_object.title,
                    new_content_unique_key
                )
                new_content_object.slug = "{}-{}".format(
                    new_content_object.slug[0:40],
                    new_content_unique_key
                )
                new_content_object.page = new_page
                new_content_object.save()

                for link in dir(content_object):
                    if link.endswith('_set') and getattr(content_object, link).__class__.__name__ == "RelatedManager" and link not in ['child_set', 'owner_set', 'link_to_page']:
                        objects = getattr(content_object, link).all()
                        for content_related_object in objects:
                            new_content_related_object = deepcopy(content_related_object)
                            new_content_related_object.pk = None
                            new_content_related_object.page = new_content_object
                            new_content_related_object.save()

            messages.add_message(request, messages.INFO, 'The page has been duplicated successfully!')
            return redirect('/admin/pages/page/{}'.format(new_page.pk))

        # Template context
        context = dict(
            page=page
        )

        # Render template
        return TemplateResponse(request, 'admin/pages/page/language_duplicate.html', context)



admin.site.register(Page, PageAdmin)

page_admin = admin.site._registry[Page]
