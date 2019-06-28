'''Base classes for the CMS admin interface.'''
from django.contrib import admin
from django.conf import settings
from reversion.admin import VersionAdmin
from watson.admin import SearchAdmin

from cms.models.base import PageBaseSearchAdapter, SearchMetaBaseSearchAdapter


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

    SEO_FIELDS = ('Search engine optimization', {
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
