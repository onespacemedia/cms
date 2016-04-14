"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""

from __future__ import unicode_literals, with_statement

from django.contrib import admin
from django.contrib.auth import get_permission_codename
from django.contrib.contenttypes.models import ContentType
from django.utils.text import capfirst
from mptt.admin import MPTTModelAdmin
from suit.admin import SortableModelAdmin

from cms import externals
from cms.apps.pages.models import (Page, PageSearchAdapter,
                                   get_registered_content)

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
    # list_editable = ['is_online']
    mptt_level_indent = 20
    sortable = 'order'

    search_adapter_cls = PageSearchAdapter

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
        # fieldsets = super(PageAdmin, self).get_fieldsets(request, obj)

        if obj is None:
            fieldsets = [
                (None, {
                    'fields': ['title', 'slug', 'parent', 'language', 'page_type']
                })
            ]

            if 'page' in request.GET:
                del fieldsets[0][1]['fields'][2]
        else:
            fieldsets = [
                (None, {
                    'fields': ['parent']
                })
            ]

        return fieldsets


admin.site.register(Page, PageAdmin)

page_admin = admin.site._registry[Page]
