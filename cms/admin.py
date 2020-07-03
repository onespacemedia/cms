"""Base classes for the CMS admin interface."""
from copy import deepcopy
from functools import update_wrapper
from random import randint

from cms.apps.pages.models import DEFAULT_LANGUAGES
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.contrib.admin.sites import NotRegistered
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

try:
    from usertools.admin import UserAdmin
except ImportError:
    from django.contrib.auth.admin import UserAdmin

from cms import externals
from cms.models.base import SearchMetaBaseSearchAdapter, PageBaseSearchAdapter
from cms.forms import CMSAdminPasswordChangeForm

# Field collections - used instead of full fieldsets to allow for custom field settings
SECURITY_FIELDS = ("requires_authentication",)
PUBLICATION_FIELDS = ("publication_date", "expiry_date", "is_online", "hide_from_search",)
PUBLICATION_FIELDS_SIMPLE = ("is_online",)
NAVIGATION_FIELDS = ("short_title", "in_navigation", "hide_from_anonymous",)
SEO_FIELDS = ("browser_title", "meta_description", "sitemap_priority", "sitemap_changefreq", "robots_index",
              "robots_follow", "robots_archive",)
OG_FIELDS = ("og_title", "og_description", "og_image")
TWITTER_FIELDS = ("twitter_card", "twitter_title", "twitter_description", "twitter_image")

def get_last_modified(obj):
    if not obj:
        return '-'

    versions = LogEntry.objects.filter(
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
    )

    if versions.count() > 0:
        latest_version = versions.first()
        date = latest_version.action_time.strftime("%Y-%m-%d %H:%M:%S")

        return date


class PublishedBaseAdmin(admin.ModelAdmin):
    change_form_template = "admin/cms/publishedmodel/change_form.html"


class OnlineBaseAdmin(PublishedBaseAdmin):
    actions = ("publish_selected", "unpublish_selected",)
    list_display = ("__str__", "is_online",)
    list_filter = ("is_online",)

    def publish_selected(self, request, queryset):
        """Publishes the selected models."""
        queryset.update(is_online=True)

    publish_selected.short_description = "Place selected %(verbose_name_plural)s online"

    def unpublish_selected(self, request, queryset):
        """Unpublishes the selected models."""
        queryset.update(is_online=False)

    unpublish_selected.short_description = "Take selected %(verbose_name_plural)s offline"


class SearchMetaBaseAdmin(OnlineBaseAdmin):
    adapter_cls = SearchMetaBaseSearchAdapter
    list_display = ("__str__", "is_online", "get_date_modified")

    fieldsets = [
        ("Publication", {
            "fields": PUBLICATION_FIELDS_SIMPLE,
            "classes": ('suit-tab', 'suit-tab-settings')
        }),
        ("Search engine optimization", {
            "fields": SEO_FIELDS,
            "classes": ('suit-tab', 'suit-tab-settings')
        }),
        ("Open Graph", {
            "fields": OG_FIELDS,
            "classes": ('suit-tab', 'suit-tab-settings')
        }),
        ("Twitter card", {
            "fields": TWITTER_FIELDS,
            "classes": ('suit-tab', 'suit-tab-settings')
        })
    ]

    def get_date_modified(self, obj):
        if externals.reversion:
            return super(SearchMetaBaseAdmin, self).get_date_modified(obj)
        return get_last_modified(obj)
        get_date_modified.short_description = 'Last modified'


if externals.reversion:
    class SearchMetaBaseAdmin(SearchMetaBaseAdmin, externals.reversion["admin.VersionMetaAdmin"]):
        pass

if externals.watson:
    class SearchMetaBaseAdmin(SearchMetaBaseAdmin, externals.watson["admin.SearchAdmin"]):
        pass


class PageBaseAdmin(SearchMetaBaseAdmin):
    prepopulated_fields = {"slug": ("title",),}
    search_fields = ("title", "short_title", "meta_description",)
    adapter_cls = PageBaseSearchAdapter

    change_form_template = "admin/pages/content/change_form.html"

    fieldsets = [
        (None, {
            "fields": ("title", "slug", "language"),
        }),
        ("Security", {
            "fields": SECURITY_FIELDS,
            "classes": ('collapse',)
        }),
        ("Publication", {
            "fields": PUBLICATION_FIELDS,
            "classes": ('collapse',)
        }),
        ("Navigation", {
            "fields": NAVIGATION_FIELDS,
            "classes": ('collapse',)
        }),
        ("Search engine optimization", {
            "fields": SEO_FIELDS,
            "classes": ('collapse',)
        }),
        ("Open Graph", {
            "fields": OG_FIELDS,
            "classes": ('collapse',)
        }),
        ("Twitter card", {
            "fields": TWITTER_FIELDS,
            "classes": ('collapse',)
        }),
    ]

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

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(PageBaseAdmin, self).get_fieldsets(request, obj)

        if obj is None:
            fieldsets = [
                (None, {
                    'fields': ['page', 'title', 'slug', 'language']
                })
            ]

            if 'page' in request.GET:
                fieldsets[0][1]['fields'].remove('page')

        return fieldsets

    def save_model(self, request, obj, form, change):
        if not obj.pk and 'page' in request.GET:
            obj.page_id = request.GET['page']

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

        page_id = obj.page.pk

        page_content_cache_keys = [
            'page_{}_{}_content'.format(page_id, language[0])
            for language in DEFAULT_LANGUAGES
            ]
        for key in page_content_cache_keys:
            cache.delete(key)

        cache.delete('page_{}_content'.format(
            page_id
        ))

        cache.delete('page_{}_children'.format(
            page_id
        ))


    def duplicate_view(self, request, *args, **kwargs):

        # Get the content object we are going to duplicate
        content_object = get_object_or_404(self.model, pk=request.GET.get('content_object', None))

        # If the user has come from the post request and its a yes...
        if request.method == 'POST' and request.POST.get('post', 'no') == 'yes':

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
            new_content_object.is_online = False
            new_content_object.save()

            for link in dir(content_object):
                if link.endswith('_set') and getattr(content_object, link).__class__.__name__ == "RelatedManager" and link not in ['child_set', 'owner_set', 'link_to_page']:
                    objects = getattr(content_object, link).all()
                    for content_related_object in objects:
                        new_content_related_object = deepcopy(content_related_object)
                        new_content_related_object.pk = None
                        new_content_related_object.page = new_content_object
                        new_content_related_object.save()

            messages.add_message(request, messages.INFO, 'The content object has been duplicated successfully!')
            return redirect('admin:{}_{}_change'.format(
                self.model._meta.app_label,
                self.model._meta.model_name
            ), *[new_content_object.pk])

        # Template context
        context = dict(
            content_object=content_object
        )

        # Render template
        return TemplateResponse(request, 'admin/pages/page/language_duplicate_translation.html', context)


class CMSUserAdmin(UserAdmin):
    change_password_form = CMSAdminPasswordChangeForm
    invite_confirm_form = CMSAdminPasswordChangeForm


try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(User, CMSUserAdmin)
