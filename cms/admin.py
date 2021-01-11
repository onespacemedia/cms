'''Base classes for the CMS admin interface.'''
from django.contrib import admin
from django.conf import settings
from django.db.models.deletion import get_candidate_relations_to_delete
from django.db.utils import DEFAULT_DB_ALIAS
from django.urls import NoReverseMatch, reverse
from reversion.admin import VersionAdmin
from watson.admin import SearchAdmin

from cms.models.base import PageBaseSearchAdapter, SearchMetaBaseSearchAdapter


def check_inline_for_admin_url(obj, inline, parent, inline_check=True):
    '''
    A function used to get the admin URL for an obj.

    Takes the object itself, an inline object and the class of the
    parent model.

    If no change URL is found, None is returned.
    '''
    # We obviously need the object to be the same type of object
    # as the inline's parent to at least get anywhere useful. We
    # catch thisstraight away and immediately return if so to save
    # time.

    if inline_check and not isinstance(obj, inline.model):
        return None

    # We've got an inline for this model. Lets check the fk_name
    # attribute on the InlineModelAdmin. If it's set we'll use
    # that, else we'll find the ForeignKey to the parent.

    obj_fk_name = getattr(inline, 'fk_name', False)
    if obj_fk_name:
        # the fk_name value is set so we assume that it will
        # resolve a parent since an inline can't be saved without
        # a parent.

        obj_parent = getattr(obj, obj_fk_name, False)
        try:
            return reverse(
                f'admin:{obj_parent._meta.app_label}_{obj_parent._meta.model_name}_change',
                args=[obj_parent.pk]
            )
        except NoReverseMatch:
            pass

    # If we make it here, the fk_name attribute was not set or the
    # parent did not resolve to an object We'll now look for
    # specifically ForeignKeys to the parent model. There can't be
    # more than one as if there were, Django would throw errors on
    # inline registration due to the lack of the fk_name
    # attribute to distinguish the two fields.

    for field in obj._meta.get_fields():
        if field.get_internal_type() in ['ForeignKey', 'OneToOneField']:
            # Follow the ForeignKey to find the related model.

            related_model = obj._meta.get_field(field.attname).remote_field.model

            if parent == related_model:
                # We've found a Foreign key to the parent, now
                # to extract the page and get its admin change URL.

                try:
                    field_value = getattr(obj, field.attname)
                except AttributeError:
                    field_value = None

                if field_value:
                    return reverse(
                        f'admin:{related_model._meta.app_label}_{related_model._meta.model_name}_change',
                        args=[field_value]
                    )


def get_admin_url(obj):
    '''
    Guesses the admin URL for an object.

    If the object has its own change view, then that will be returned.

    It will then check to see if it is an inline on another object's
    change view.

    Failing that, it will see if it is an inline registered to a Page
    (with page_admin.register_content_inline).
    '''
    # We first of all just try and get an admin URL for the object that has
    # been passed to us.
    try:
        return reverse(
            f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
            args=[obj.pk]
        )
    except NoReverseMatch:
        pass

    # If we can't get and admin change URL for the object directly, we'll
    # now see if it's an inline with a parent model. If so, we'll return
    # the parent model's change URL
    # Having been given an arbitrary object, the only way we can work explicitly
    # out what the object's parent is, without making any assumptions, is by
    # looking through all registered models and tunneling down.

    for model_cls, model_admin in admin.site._registry.items():
        # Check if the model we're looking at has any inlines. If it hasn't had
        # any inlines set, model.inlines returns an empty array.
        inlines = model_admin.inlines

        # Loop over the model's inlines and check for references to our obj
        for inline in inlines:
            url = check_inline_for_admin_url(obj, inline, model_cls)

            if url:
                return url

    if 'cms.apps.pages' in settings.INSTALLED_APPS:
        from cms.apps.pages.admin import page_admin
        from cms.apps.pages.models import Page
        # If we've made it here, then obj is neither an object with an admin
        # change URL nor is it an inline of a registered model with an admin
        # change URL. Lets check inlines registered with page_admin.
        for _, inline in page_admin.content_inlines:
            # page_admin.content_inlines is a list of tuples. The first value
            # is the ContentType and the second is the inline InlineModelAdmin
            # used to register the model.
            # We're going to check for ForeignKeys to 'pages.Page' since they'll
            # have to have one to be registered as a content inline.

            url = check_inline_for_admin_url(obj, inline, Page)

            if url:
                return url
        # You can use the same logic that tests for a ContentBaseInline page to test for a ContentBae page

        # If none of the above work then we're really out of options. Just
        # return None and let our caller handle this.
        return check_inline_for_admin_url(obj, None, Page, inline_check=False)


def get_related_objects_admin_urls(obj):
    related_objs = []

    for related in get_candidate_relations_to_delete(obj._meta):
        related_objs = related_objs + list(related.related_model._base_manager.using(DEFAULT_DB_ALIAS).filter(
            **{"%s__in" % related.field.name: [obj]}
        ))

    return [
        {
            'title': str(obj),
            'model_name': obj._meta.verbose_name,
            'admin_url': get_admin_url(obj),
        } for obj in related_objs
    ]


class PublishedBaseAdmin(admin.ModelAdmin):
    '''Base admin class for models with publication controls.'''

    change_form_template = 'admin/cms/publishedmodel/change_form.html'


class OnlineBaseAdmin(PublishedBaseAdmin):
    '''Base admin class for OnlineModelBase instances.'''

    actions = ('publish_selected', 'unpublish_selected',)

    list_display = ('__str__', 'is_online',)

    list_filter = ('is_online',)

    PUBLICATION_FIELDS = ('Publication', {
        'fields': ('is_online',),
        'classes': ('collapse',),
    })

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['is_online'].initial = getattr(settings, 'ONLINE_DEFAULT', True)
        return form

    # Custom admin actions.
    def publish_selected(self, request, queryset):
        '''Publishes the selected models.'''
        queryset.update(is_online=True)
    publish_selected.short_description = 'Place selected %(verbose_name_plural)s online'

    def unpublish_selected(self, request, queryset):
        '''Unpublishes the selected models.'''
        queryset.update(is_online=False)
    unpublish_selected.short_description = 'Take selected %(verbose_name_plural)s offline'


class SearchMetaBaseAdmin(OnlineBaseAdmin, VersionAdmin, SearchAdmin):
    '''Base admin class for SearchMetaBase models.'''

    adapter_cls = SearchMetaBaseSearchAdapter

    list_display = ('__str__', 'is_online',)

    SEO_FIELDS = ('SEO', {
        'fields': ('browser_title', 'meta_description', 'sitemap_priority', 'sitemap_changefreq', 'robots_index', 'robots_follow', 'robots_archive',),
        'classes': ('collapse',),
    })

    OPENGRAPH_FIELDS = ('Open Graph', {
        'fields': ('og_title', 'og_description', 'og_image'),
        'classes': ('collapse',)
    })

    OPENGRAPH_TWITTER_FIELDS = ('Twitter card', {
        'fields': ('twitter_card', 'twitter_title', 'twitter_description', 'twitter_image'),
        'classes': ('collapse',)
    })


class PageBaseAdmin(SearchMetaBaseAdmin):
    '''Base admin class for PageBase models.'''

    prepopulated_fields = {'slug': ('title',), }

    search_fields = ('title', 'short_title', 'meta_description',)

    adapter_cls = PageBaseSearchAdapter

    TITLE_FIELDS = (None, {
        'fields': ('title', 'slug',),
    })

    NAVIGATION_FIELDS = ('Navigation', {
        'fields': ('short_title',),
        'classes': ('collapse',),
    })

    fieldsets = [
        TITLE_FIELDS,
        OnlineBaseAdmin.PUBLICATION_FIELDS,
        NAVIGATION_FIELDS,
        SearchMetaBaseAdmin.SEO_FIELDS,
        SearchMetaBaseAdmin.OPENGRAPH_FIELDS,
        SearchMetaBaseAdmin.OPENGRAPH_TWITTER_FIELDS
    ]
