"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""

from __future__ import unicode_literals, with_statement

from functools import cmp_to_key
import json
from copy import deepcopy

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth import get_permission_codename
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.urlresolvers import reverse
from django.conf.urls import patterns, url
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, models
from django.db.models import F, Q
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.utils import six
from django import forms

from cms import debug, externals
from cms.admin import PageBaseAdmin
from cms.apps.pages.models import Page, get_registered_content, PageSearchAdapter, Country, CountryGroup



# Used to track references to and from the JS sitemap.
PAGE_FROM_KEY = "from"
PAGE_FROM_SITEMAP_VALUE = "sitemap"


# The GET parameter used to indicate content type.
PAGE_TYPE_PARAMETER = "type"


class PageAdmin(PageBaseAdmin):

    list_display = ("__str__", "is_online",)

    """Admin settings for Page models."""

    new_fieldsets = [
        (None, {
            "fields": ("title", "slug", "parent"),
        }),
        ("Security", {
            "fields": ("requires_authentication",),
        }),
        ("Publication", {
            "fields": ("publication_date", "expiry_date", "is_online"),
            "classes": ("collapse",)
        }),
        ("Navigation", {
            "fields": ("short_title", "in_navigation", "hide_from_anonymous"),
            "classes": ("collapse",)
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

    def get_queryset(self, request):
        return super(PageAdmin, self).get_queryset(request).filter(is_content_object=False)

    def get_object(self, request, object_id, from_field=None):
        queryset = super(PageAdmin, self).get_queryset(request)
        model = queryset.model
        field = model._meta.pk if from_field is None else model._meta.get_field(
            from_field)
        try:
            object_id = field.to_python(object_id)
            return queryset.get(**{field.name: object_id})
        except (model.DoesNotExist, ValidationError, ValueError):
            return None

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
        # Patch the admin class's index template.
        self.admin_site.index_template = "admin/pages/dashboard.html"
        # Prepare to register some content inlines.
        self.content_inlines = []
        # Register all page inlines.
        for content_cls in get_registered_content():
            self._register_page_inline(content_cls)

        if externals.reversion:
            self.list_display = ("__str__", "last_modified", "is_online",)

    def register_content_inline(self, content_cls, inline_admin):
        """Registers an inline model with the page admin."""
        self.content_inlines.append((content_cls, inline_admin))
        self._register_page_inline(inline_admin.model)

    def get_inline_instances(self, request, obj=None):
        """Returns all the inline instances for this PageAdmin."""
        try:
            inline_instances = super(PageAdmin, self).get_inline_instances(request, obj)
        except TypeError:
            inline_instances = super(PageAdmin, self).get_inline_instances(request)
        # Add on the relevant content inlines.
        obj = getattr(request, "_admin_change_obj", None)  # HACK: Retrieve the page from the change view.
        content_cls = self.get_page_content_cls(request, obj)
        for cls, inline in self.content_inlines:
            if cls == content_cls:
                inline_instances.append(inline(self.model, self.admin_site))
        # All done!
        return inline_instances

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

    def get_page_content_cls(self, request, obj=None):
        """Retrieves the page content type slug."""
        if PAGE_TYPE_PARAMETER in request.GET:
            return ContentType.objects.get_for_id(request.GET[PAGE_TYPE_PARAMETER]).model_class()
        if obj and obj.content_type:
            return obj.content_type.model_class()
        raise Http404("You must specify a page content type.")

    def get_fieldsets(self, request, obj=None):
        """Generates the custom content fieldsets."""
        content_cls = self.get_page_content_cls(request, obj)
        content_fields = [field.name for field in content_cls._meta.fields + content_cls._meta.many_to_many if field.name != "page"]
        fieldsets = super(PageAdmin, self).get_fieldsets(request, obj)
        if content_fields:
            content_fieldsets = content_cls.fieldsets or [
                ("Page content", {
                    "fields": content_fields,
                }),
            ]
            fieldsets = list(fieldsets[0:1]) + content_fieldsets + list(fieldsets[1:])
        return fieldsets

    def get_all_children(self, page):
        """Returns all the children for a page."""
        children = []

        def do_get_all_children(page):
            for child in page.children:
                children.append(child)
                do_get_all_children(child)
        do_get_all_children(page)
        return children

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
        content_cls = self.get_page_content_cls(request, obj)
        form_attrs = {}
        for field in content_cls._meta.fields + content_cls._meta.many_to_many:
            if field.name == "page":
                continue
            form_field = self.formfield_for_dbfield(field, request=request)
            # HACK: add in the initial value. No other way to pass this on.
            if obj:
                try:
                    form_field.initial = getattr(obj.content, field.name, "")
                    if isinstance(field, models.ManyToManyField):
                        form_field.initial = form_field.initial.all()
                except content_cls.DoesNotExist:
                    pass  # This means that we're in a reversion recovery, or something weird has happened to the database.

            if field.name in getattr(content_cls, "filter_horizontal", ()):
                form_field.widget = FilteredSelectMultiple(
                    field.verbose_name,
                    is_stacked=False,
                )
            # Store the field.
            form_attrs[field.name] = form_field
        if six.PY2:
            ContentForm = type(six.binary_type("{}Form").format(self.__class__.__name__), (forms.ModelForm,), form_attrs)
        else:
            ContentForm = type(six.text_type("{}Form".format(self.__class__.__name__)), (forms.ModelForm,), form_attrs)
        defaults = {"form": ContentForm}
        defaults.update(kwargs)

        if obj and obj.is_content_object:
            self.prepopulated_fields = {}
            self.fieldsets[0][1]['fields'] = ('title',)
        else:
            self.prepopulated_fields = {"slug": ("title",), }
            self.fieldsets[0][1]['fields'] = ("title", "slug", "parent")

        PageForm = super(PageAdmin, self).get_form(request, obj, **defaults)

        # HACK: Need to limit parents field based on object. This should be done in
        # formfield_for_foreignkey, but that method does not know about the object instance.
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
                    parent_choices.append((page.id, " \u203a ".join(u"{}".format(breadcrumb.title) for breadcrumb in self.get_breadcrumbs(page))))
        else:
            parent_choices = []

        if not parent_choices:
            parent_choices = (("", "---------"),)

        if obj and not obj.is_content_object:
            PageForm.base_fields["parent"].choices = parent_choices
        elif not obj:
            PageForm.base_fields["parent"].choices = parent_choices

        # Return the completed form.
        return PageForm

    def save_model(self, request, obj, form, change):
        """Saves the model and adds its content fields."""
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
            if field.name == "page":
                continue
            setattr(content_obj, field.name, form.cleaned_data[field.name])
        # Save the model.
        super(PageAdmin, self).save_model(request, obj, form, change)
        # Save the page content.
        content_obj.page = obj
        content_obj.save()

        # Now save m2m fields.
        for field in content_obj._meta.many_to_many:
            setattr(content_obj, field.name, form.cleaned_data[field.name])

        obj.content = content_obj

    # Permissions.

    def has_add_content_permission(self, request, model):
        """Checks whether the given user can edit the given content model."""
        opts = model._meta
        return request.user.has_perm("{0}.{1}".format(opts.app_label, get_permission_codename('add', opts)))

    def has_add_permission(self, request):
        """Checks whether the user can edits pages and at least one content model."""
        if not super(PageAdmin, self).has_add_permission(request):
            return False
        for content_model in get_registered_content():
            if self.has_add_content_permission(request, content_model):
                return True
        return False

    def has_change_permission(self, request, obj=None):
        """Checks whether the user can edit the page and associated content model."""
        if not super(PageAdmin, self).has_change_permission(request, obj):
            return False
        if obj:
            content_model = ContentType.objects.get_for_id(obj.content_type_id).model_class()
            content_opts = content_model._meta
            return request.user.has_perm("{0}.{1}".format(
                content_opts.app_label,
                get_permission_codename('change', content_opts)
            ))
        return True

    def has_delete_permission(self, request, obj=None):
        """Checks whether the user can delete the page and associated content model."""
        if not super(PageAdmin, self).has_delete_permission(request, obj):
            return False
        if obj:
            content_model = ContentType.objects.get_for_id(obj.content_type_id).model_class()
            content_opts = content_model._meta
            return request.user.has_perm("{0}.{1}".format(
                content_opts.app_label,
                get_permission_codename('delete', content_opts)
            ))
        return True

    # Custom views.

    def patch_response_location(self, request, response):
        """Perpetuates the 'from' key in all redirect responses."""
        if isinstance(response, HttpResponseRedirect):
            if PAGE_FROM_KEY in request.GET:
                response["Location"] += "?%s=%s" % (PAGE_FROM_KEY, request.GET[PAGE_FROM_KEY])
        return response

    def changelist_view(self, request, *args, **kwargs):
        """Redirects to the sitemap, if appropriate."""
        if PAGE_FROM_KEY in request.GET:
            redirect_slug = request.GET[PAGE_FROM_KEY]
            if redirect_slug == PAGE_FROM_SITEMAP_VALUE:
                return redirect("admin:index")
        return super(PageAdmin, self).changelist_view(request, *args, **kwargs)

    def change_view(self, request, object_id, *args, **kwargs):
        """Uses only the correct inlines for the page."""
        # HACK: Add the current page to the request to pass to the get_inline_instances() method.
        page = get_object_or_404(self.model, id=object_id)
        request._admin_change_obj = page

        extra_context = {}

        if not page.is_content_object:
            # Get all of the language pages
            extra_context['language_pages'] = Page.objects.filter(
                Q(pk=page.pk) |
                Q(owner=page, is_content_object=True)
            ).order_by('-country_group')
        else:
            extra_context['language_pages'] = Page.objects.filter(
                Q(pk=page.owner.pk) |
                Q(owner=page.owner, is_content_object=True)
            ).order_by('-country_group')

        extra_context['display_language_options'] = False
        if 'cms.middleware.LocalisationMiddleware' in settings.MIDDLEWARE_CLASSES:
            extra_context['display_language_options'] = True

        # Call the change view.
        return super(PageAdmin, self).change_view(request, object_id, extra_context=extra_context, *args, **kwargs)

    def revision_view(self, request, object_id, *args, **kwargs):
        """Load up the correct content inlines."""
        # HACK: Add the current page to the request to pass to the get_inline_instances() method.
        page = get_object_or_404(self.model, id=object_id)
        request._admin_change_obj = page
        # Call the change view.
        return super(PageAdmin, self).revision_view(request, object_id, *args, **kwargs)

    def add_view(self, request, *args, **kwargs):
        """Ensures that a valid content type is chosen."""
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
                    url = request.path + "?" + query_string
                    content_type_context = {
                        "name": content_type._meta.verbose_name,
                        "icon": staticfiles_storage.url(content_type.icon),
                        "url": url,
                        "classifier": content_type.classifier
                    }
                    content_types.append(content_type_context)
            # Shortcut for when there is a single content type.
            if len(content_types) == 1:
                return redirect(content_types[0]["url"])
            # Render the select page template.
            context = {
                "title": "Select page type",
                "content_types": content_types
            }

            return render(request, "admin/pages/page/select_page_type.html", context)
        else:
            if not self.has_add_content_permission(request, ContentType.objects.get_for_id(request.GET[PAGE_TYPE_PARAMETER]).model_class()):
                raise PermissionDenied("You are not allowed to add pages of that content type.")
        return super(PageAdmin, self).add_view(request, *args, **kwargs)

    def response_add(self, request, *args, **kwargs):
        """Redirects to the sitemap if appropriate."""
        response = super(PageAdmin, self).response_add(request, *args, **kwargs)
        return self.patch_response_location(request, response)

    def response_change(self, request, *args, **kwargs):
        """Redirects to the sitemap if appropriate."""
        response = super(PageAdmin, self).response_change(request, *args, **kwargs)
        return self.patch_response_location(request, response)

    def delete_view(self, request, *args, **kwargs):
        """Redirects to the sitemap if appropriate."""
        response = super(PageAdmin, self).delete_view(request, *args, **kwargs)
        return self.patch_response_location(request, response)

    def get_urls(self):
        """Adds in some custom admin URLs."""
        admin_view = self.admin_site.admin_view
        return patterns(
            "",
            url("^sitemap.json$", admin_view(self.sitemap_json_view), name="pages_page_sitemap_json"),
            url("^move-page/$", admin_view(self.move_page_view), name="pages_page_move_page"),
            url("^(?P<page>\d+)/duplicate/$", admin_view(self.duplicate_for_country_group), name="pages_page_duplicate_page"),
        ) + super(PageAdmin, self).get_urls()

    @debug.print_exc
    def sitemap_json_view(self, request):
        """Returns a JSON data structure describing the sitemap."""
        # Get the homepage.
        homepage = request.pages.homepage
        # Compile the initial data.
        data = {
            "canAdd": self.has_add_permission(request),
            "createHomepageUrl": reverse("admin:pages_page_add") + "?{0}={1}".format(PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
            "moveUrl": reverse("admin:pages_page_move_page") or None,
            "addUrl": reverse("admin:pages_page_add") + "?{0}={1}&parent=__id__".format(PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
            "changeUrl": reverse("admin:pages_page_change", args=("__id__",)) + "?{0}={1}".format(PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
            "deleteUrl": reverse("admin:pages_page_delete", args=("__id__",)) + "?{0}={1}".format(PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
        }
        # Add in the page data.
        if homepage:
            def sitemap_entry(page):
                children = []
                for child in page.children:
                    children.append(sitemap_entry(child))
                return {
                    "isOnline": page.is_online,
                    "id": page.id,
                    "title": str(page),
                    "children": children,
                    "canChange": self.has_change_permission(request, page),
                    "canDelete": self.has_delete_permission(request, page),
                }
            data["entries"] = [sitemap_entry(homepage)]
        else:
            data["entries"] = []
        # Render the JSON.
        response = HttpResponse(content_type="application/json; charset=utf-8")
        json.dump(data, response)
        return response

    @transaction.atomic
    @debug.print_exc
    def move_page_view(self, request):
        """Moves a page up or down."""
        # Check that the user has permission to move pages.
        if not self.has_change_permission(request):
            return HttpResponseForbidden("You do not have permission to move this page.")

        # Lock entire table.
        existing_pages_list = Page.objects.all().exclude(
            is_content_object=True,
        ).select_for_update().values(
            "id",
            "parent_id",
            "left",
            "right",
            "title"
        ).order_by("left")
        existing_pages = dict(
            (page["id"], page)
            for page
            in existing_pages_list
        )

        # Get the page.
        page = existing_pages[int(request.POST["page"])]
        parent_id = page["parent_id"]

        # Get all the siblings.
        siblings = [s for s in existing_pages_list if s["parent_id"] == parent_id]

        # Find the page to swap.
        direction = request.POST["direction"]

        if direction == "up":
            siblings.reverse()
        elif direction == "down":
            pass
        else:
            raise ValueError("Direction should be 'up' or 'down'.")

        sibling_iter = iter(siblings)
        for sibling in sibling_iter:
            if sibling["id"] == page["id"]:
                break
        try:
            other_page = next(sibling_iter)
        except StopIteration:
            return HttpResponse("Page could not be moved, as nothing to swap with.")

        # Put the pages in order.
        first_page, second_page = sorted((page, other_page), key=lambda p: p["left"])

        # Excise the first page.
        Page.objects.filter(left__gte=first_page["left"], right__lte=first_page["right"]).update(
            left=F("left") * -1,
            right=F("right") * -1,
        )

        # Move the other page.
        branch_width = first_page["right"] - first_page["left"] + 1
        Page.objects.filter(left__gte=second_page["left"], right__lte=second_page["right"]).update(
            left=F("left") - branch_width,
            right=F("right") - branch_width,
        )

        # Put the page back in.
        second_branch_width = second_page["right"] - second_page["left"] + 1
        Page.objects.filter(left__lte=-first_page["left"], right__gte=-first_page["right"]).update(
            left=(F("left") - second_branch_width) * -1,
            right=(F("right") - second_branch_width) * -1,
        )

        # Update all content models to match the left and right of their parents.
        existing_pages_list = Page.objects.all().exclude(
            is_content_object=False,
        ).select_for_update().values(
            "id",
            "parent_id",
            "owner",
            "left",
            "right",
            "title"
        ).order_by("left")

        for child_page in existing_pages_list:
            child_page.update(
                left=F('owner__left'),
                right=F('owner__right'),
            )

        # Report back.
        return HttpResponse("Page #%s was moved %s." % (page["id"], direction))

    def duplicate_for_country_group(self, request, *args, **kwargs):
        # Get the current page
        original_page = get_object_or_404(Page, pk=kwargs.get('page', None))
        original_content = original_page.content

        if request.method == 'POST':

            with externals.watson.context_manager("update_index")():
                page = deepcopy(original_page)
                page.pk = None
                page.is_content_object = True
                page.owner = original_page
                page.country_group = CountryGroup.objects.get(pk=request.POST.get('country_group'))
                page.save()

                content = deepcopy(original_content)
                content.pk = None
                content.page = page
                content.save()

                # for field in original_page._meta.get_fields_with_model():
                #
                #     if RelatedField in inspect.getmro(field[0].__class__):
                #         print field
                #
                # for attr in dir(original_page):
                #     if attr.endswith('_set'):
                #         print attr

                # links = [rel.get_accessor_name() for rel in original_page._meta.get_all_related_objects()]

                for link in dir(original_page):
                    if link.endswith('_set') and getattr(original_page, link).__class__.__name__ == "RelatedManager" and link not in ['child_set', 'owner_set', 'link_to_page']:
                        objects = getattr(original_page, link).all()
                        for page_object in objects:
                            new_object = deepcopy(page_object)
                            new_object.pk = None
                            new_object.page = page
                            new_object.save()

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


class CountryGroupAdmin(admin.ModelAdmin):
    pass


class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'group')


admin.site.register(Page, PageAdmin)

if 'cms.middleware.LocalisationMiddleware' in settings.MIDDLEWARE_CLASSES:
    admin.site.register(Country, CountryAdmin)
    admin.site.register(CountryGroup, CountryGroupAdmin)

page_admin = admin.site._registry[Page]
