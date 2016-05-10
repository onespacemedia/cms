"""Base classes for the CMS admin interface."""

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.admin.sites import NotRegistered
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

try:
    from usertools.admin import UserAdmin
except ImportError:
    from django.contrib.auth.admin import UserAdmin

from cms import externals
from cms.models.base import SearchMetaBaseSearchAdapter, PageBaseSearchAdapter
from cms.forms import CMSAdminPasswordChangeForm


class PublishedBaseAdmin(admin.ModelAdmin):

    """Base admin class for published models."""

    change_form_template = "admin/cms/publishedmodel/change_form.html"


class OnlineBaseAdmin(PublishedBaseAdmin):

    """Base admin class for OnlineModelBase instances."""

    actions = ("publish_selected", "unpublish_selected",)

    list_display = ("__str__", "is_online",)

    list_filter = ("is_online",)

    PUBLICATION_FIELDS = ("Publication", {
        "fields": ("is_online",),
        "classes": ("collapse",),
    })

    # Custom admin actions.

    def publish_selected(self, request, queryset):
        """Publishes the selected models."""
        queryset.update(is_online=True)
    publish_selected.short_description = "Place selected %(verbose_name_plural)s online"

    def unpublish_selected(self, request, queryset):
        """Unpublishes the selected models."""
        queryset.update(is_online=False)
    unpublish_selected.short_description = "Take selected %(verbose_name_plural)s offline"


class SearchMetaBaseAdmin(OnlineBaseAdmin):

    """Base admin class for SearchMetaBase models."""

    adapter_cls = SearchMetaBaseSearchAdapter

    list_display = ("__str__", "is_online",)

    SEO_FIELDS = ("Search engine optimization", {
        "fields": ("browser_title", "meta_description", "sitemap_priority", "sitemap_changefreq", "robots_index", "robots_follow", "robots_archive",),
        "classes": ("collapse",),
    })

    OPENGRAPH_FIELDS = ("Open Graph", {
        "fields": ("og_title", "og_description", "og_image"),
        "classes": ("collapse",)
    })

    OPENGRAPH_TWITTER_FIELDS = ("Twitter card", {
        "fields": ("twitter_card", "twitter_title", "twitter_description", "twitter_image"),
        "classes": ("collapse",)
    })


if externals.reversion:
    class SearchMetaBaseAdmin(SearchMetaBaseAdmin, externals.reversion["admin.VersionMetaAdmin"]):
        list_display = SearchMetaBaseAdmin.list_display + ("get_date_modified",)


if externals.watson:
    class SearchMetaBaseAdmin(SearchMetaBaseAdmin, externals.watson["admin.SearchAdmin"]):
        pass


class PageBaseAdmin(SearchMetaBaseAdmin):

    """Base admin class for PageBase models."""

    prepopulated_fields = {"slug": ("title",), }

    search_fields = ("title", "short_title", "meta_description",)

    adapter_cls = PageBaseSearchAdapter

    TITLE_FIELDS = (None, {
        "fields": ("title", "slug",),
    })

    NAVIGATION_FIELDS = ("Navigation", {
        "fields": ("short_title",),
        "classes": ("collapse",),
    })

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


class ContentBaseAdmin(PageBaseAdmin):

    """Base admin for ContentBase derivatives."""

    # Special template - we override the breadcrumbs to avoid confusion. We
    # want to appear that we're a sub-level of a Page, rather than the admin
    # for <someapp>/<some_content_base_derivative>.
    change_form_template = "admin/pages/contentbase/change_form.html"

    delete_confirmation_template = "admin/pages/contentbase/delete_confirmation.html"

    def response_add(self, request, obj, post_url_continue=None):
        """Override the standard redirect URL after a save - we want to return
        people to the page's change form, not the one for the ContentBase
        derivative."""
        if "_continue" in request.POST:
            return super(ContentBaseAdmin, self).response_change(request, obj)

        page_url = reverse("admin:pages_page_change", args=[obj.page.pk])
        return HttpResponseRedirect(page_url)

    def response_change(self, request, obj):
        """Override the standard redirect URL after a save - we want to return
        people to the page's change form, not the one for the ContentBase
        derivative."""
        if "_continue" in request.POST:
            return super(ContentBaseAdmin, self).response_change(request, obj)

        page_url = reverse("admin:pages_page_change", args=[obj.page.pk])
        return HttpResponseRedirect(page_url)

    def delete_view(self, request, object_id, extra_context=None):
        """Redirect to the content object's page admin on deletion."""
        this_object = self.get_object(request, object_id)
        # In the unlikely case that this doesn't exist...
        if not this_object:
            return super(ContentBaseAdmin, self).delete_view(request, object_id, extra_context)

        page_object_id = this_object.page_id

        response = super(ContentBaseAdmin, self).delete_view(request, object_id, extra_context)

        # If the return type of the original delete_view was a redirect, then
        # use the deleted content's page admin URL.
        if isinstance(response, HttpResponseRedirect):
            return HttpResponseRedirect(reverse("admin:pages_page_change", args=[page_object_id]))

        return response


class CMSUserAdmin(UserAdmin):
    change_password_form = CMSAdminPasswordChangeForm
    invite_confirm_form = CMSAdminPasswordChangeForm

try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(User, CMSUserAdmin)
