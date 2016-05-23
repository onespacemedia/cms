"""Base classes for the CMS admin interface."""

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.admin.sites import NotRegistered

try:
    from usertools.admin import UserAdmin
except ImportError:
    from django.contrib.auth.admin import UserAdmin

from cms import externals
from cms.models.base import SearchMetaBaseSearchAdapter, PageBaseSearchAdapter
from cms.forms import CMSAdminPasswordChangeForm

# Field collections - used instead of full fieldsets to allow for custom field settings
SECURITY_FIELDS = ("requires_authentication",)
PUBLICATION_FIELDS = ("publication_date", "expiry_date", "is_online",)
PUBLICATION_FIELDS_SIMPLE = ("is_online",)
NAVIGATION_FIELDS = ("short_title", "in_navigation", "hide_from_anonymous",)
SEO_FIELDS = ("browser_title", "meta_description", "sitemap_priority", "sitemap_changefreq", "robots_index",
              "robots_follow", "robots_archive",)
OG_FIELDS = ("og_title", "og_description")
TWITTER_FIELDS = ("twitter_card", "twitter_title", "twitter_description")


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
    list_display = ("__str__", "is_online",)

    suit_form_tabs = (('content', 'Content'), ('settings', 'Settings'),)

    def get_fields(self, request, obj=None):
        # Get base fields
        form = self.get_form(request, obj, fields=None)
        fields = list(form.base_fields) + list(self.get_readonly_fields(request, obj))

        # Create new fields array
        new_fields = []

        # Loop the base fields and only add those we want
        for field in fields:
            if field not in SEO_FIELDS + OG_FIELDS + TWITTER_FIELDS + PUBLICATION_FIELDS_SIMPLE:
                new_fields.append(field)

        # Return new fields
        return new_fields

    def get_fieldsets(self, request, obj=None):
        # If we have pre-defined fieldsets, add the admin fields to those for the user
        if self.fieldsets:
            return [
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
                   ] + self.fieldsets

        # We have no fieldsets, so ust generate a basic admin content field split
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
        fields = self.get_fields(request, obj)
        if fields:
            fieldsets.append(
                ("Content", {'fields': fields, "classes": ('suit-tab', 'suit-tab-content')})
            )

        return fieldsets


if externals.reversion:
    class SearchMetaBaseAdmin(SearchMetaBaseAdmin, externals.reversion["admin.VersionMetaAdmin"]):
        list_display = SearchMetaBaseAdmin.list_display + ("get_date_modified",)


if externals.watson:
    class SearchMetaBaseAdmin(SearchMetaBaseAdmin, externals.watson["admin.SearchAdmin"]):
        pass


class PageBaseAdmin(SearchMetaBaseAdmin):
    prepopulated_fields = {"slug": ("title",), }
    search_fields = ("title", "short_title", "meta_description",)
    adapter_cls = PageBaseSearchAdapter
    suit_form_tabs = (('content', 'Content'), ('settings', 'Settings'),)

    fieldsets = [
        (None, {
            "fields": ("title", "slug",),
            "classes": ('suit-tab', 'suit-tab-content')
        }),
        ("Security", {
            "fields": SECURITY_FIELDS,
            "classes": ('suit-tab', 'suit-tab-settings')
        }),
        ("Publication", {
            "fields": PUBLICATION_FIELDS,
            "classes": ('suit-tab', 'suit-tab-settings')
        }),
        ("Navigation", {
            "fields": NAVIGATION_FIELDS,
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
        }),
    ]

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


class CMSUserAdmin(UserAdmin):
    change_password_form = CMSAdminPasswordChangeForm
    invite_confirm_form = CMSAdminPasswordChangeForm

try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(User, CMSUserAdmin)
