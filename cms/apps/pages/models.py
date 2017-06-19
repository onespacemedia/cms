# coding=utf8
"""Core models used by the CMS."""
from __future__ import unicode_literals

from django.conf import settings
from django.core.cache import cache

from cms import externals, sitemaps
from cms.models import PageBase, PageBaseSearchAdapter
from cms.models.managers import publication_manager
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.text import mark_safe
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from threadlocals.threadlocals import get_current_request


# ISO 639-1 codes.
DEFAULT_LANGUAGES = [
    ('ar', ['Arabic', 'العربية']),
    ('bn', ['Bengali', 'বাংলা']),
    ('cs', ['Czech', 'Čeština']),
    ('da', ['Danish', 'Dansk']),
    ('nl', ['Dutch', 'Nederlands']),
    ('en', ['English', 'English']),
    ('fi', ['Finnish', 'Suomi']),
    ('fr', ['French', 'Français']),
    ('de', ['German', 'Deutsch']),
    ('el', ['Greek', 'ελληνικά']),
    ('hi', ['Hindi', 'हिन्दी']),
    ('it', ['Italian', 'Italiano']),
    ('ja', ['Japanese', '日本語']),
    ('jv', ['Javanese', 'ꦧꦱꦗꦮ']),
    ('zh', ['Mandarin', '中文']),
    ('pa', ['Panjabi', 'ਪੰਜਾਬੀ']),
    ('pl', ['Polish', 'Język polski']),
    ('pt', ['Portugese', 'Português']),
    ('ru', ['Russian', 'Русский']),
    ('es', ['Spanish', 'Español']),
    ('sv', ['Swedish', 'Svenska']),
]

LANGUAGES = getattr(settings, 'PAGE_LANGUAGES', DEFAULT_LANGUAGES)

LANGUAGES_ENGLISH = [
    (x[0], x[1][0])
    for x in LANGUAGES
]

LANGUAGES_ENGLISH_DICTIONARY = {
    x[0]: x[1][0]
    for x in LANGUAGES
}

DEFAULT_LANGUAGE = 'en'


@python_2_unicode_compatible
class Page(MPTTModel):

    """A page within the site."""

    # Hierarchy fields.
    objects = TreeManager()

    parent = TreeForeignKey(
        'self',
        blank=True,
        null=True,
        related_name="child_set",
    )

    # Sortable property
    order = models.PositiveIntegerField()

    @cached_property
    def content(self):
        request = get_current_request()
        language = getattr(request, 'language', DEFAULT_LANGUAGE)

        # If we have no language, use default
        if language is None:
            language = DEFAULT_LANGUAGE

        # Check to see if we have a temp language override set
        if hasattr(request, 'temp_language'):
            language = request.temp_language
            del request.temp_language

        # Create django cache key
        cache_key = 'page_{}_{}_content'.format(
            self.pk,
            language
        )

        # Get content object from cache
        object = cache.get(cache_key)
        if object:
            return object

        # Store all objects in cache to speed up query
        objects_cache_key = 'page_{}_content'.format(
            self.pk
        )

        objects = cache.get(objects_cache_key)

        if not objects:

            objects = []

            # Get the content for this page.
            for model in get_registered_content():
                query_objects = model.objects.filter(
                    page_id=self.pk
                )

                for object in query_objects:
                    objects.append(object)

            cache.set('page_{}_content'.format(
                self.pk
            ), objects)

        # Loop the objects and try to return one that matches the current language,
        # otherwise, use default or fail
        for object in objects:
            cache.set('page_{}_{}_content'.format(
                self.pk,
                object.language
            ), object)

        request_language_content = cache.get('page_{}_{}_content'.format(
            self.pk,
            language
        ))

        if request_language_content:
            return request_language_content

        default_language_content = cache.get('page_{}_{}_content'.format(
            self.pk,
            DEFAULT_LANGUAGE
        ))

        if default_language_content:
            return default_language_content

        return None

    @cached_property
    def slug(self):
        if not hasattr(self.content, 'slug'):
            return ''

        return self.content.slug

    @property
    def navigation(self):
        """The sub-navigation of this page."""
        return self.get_children()

    @cached_property
    def content_objects(self):
        # Are there any content objects in this language?
        content_objects = []

        for model in get_registered_content():
            objects = model.objects.filter(
                page_id=self.pk,
                is_online=True,
            )
            content_objects.extend(objects)

        return content_objects

    def languages(self):
        # TODO: Change this.
        output = []

        content_objects = self.content_objects

        if len(content_objects) > 0:
            for content_object in content_objects:
                content_type = ContentType.objects.get_for_model(content_object._meta.model)

                output.append('<a href="{}">{}</a>'.format(
                    reverse('admin:{}_{}_change'.format(
                        content_type.app_label,
                        content_type.model
                    ), args=[content_object.pk]),
                    content_object.language.upper()
                ))

        return mark_safe(' | '.join(output))

    def reverse(self, view_func, args=None, kwargs=None):
        """Performs a reverse URL lookup."""
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        urlconf = ContentType.objects.get_for_model(
            self.content
        ).model_class().urlconf

        return self.content.get_absolute_url() + urlresolvers.reverse(
            view_func,
            args=args,
            kwargs=kwargs,
            urlconf=urlconf,
            prefix=""
        )

    # Standard model methods.

    def last_modified(self):
        if externals.reversion:
            import reversion
            versions = reversion.get_for_object(self)
            if versions.count() > 0:
                latest_version = versions[:1][0]
                return "{} by {}".format(
                    latest_version.revision.date_created.strftime("%Y-%m-%d %H:%M:%S"),
                    latest_version.revision.user
                )
        return "-"

    def __str__(self):
        content = self.content

        if content:
            import six
            return six.text_type(content.title)
        return 'N/A'

    # It is required to rebuild tree after save, when using order for mptt-tree
    def save(self, *args, **kwargs):
        super(Page, self).save(*args, **kwargs)
        Page.objects.rebuild()

    class MPTTMeta:
        order_insertion_by = ['order']


externals.historylinks("register", Page)


class PageSitemap(sitemaps.PageBaseSitemap):

    """Sitemap for page models."""

    model = Page

    def items(self):
        """Only lists items that are marked as indexable."""
        return filter_indexable_pages(super(PageSitemap, self).items())


sitemaps.register(Page, sitemap_cls=PageSitemap)


class PageSearchAdapter(PageBaseSearchAdapter):

    """Search adapter for Page models."""

    def get_content(self, obj):
        """Returns the search text for the page."""
        content_obj = obj.content

        return u" ".join((
            super(PageSearchAdapter, self).get_content(obj),
            self.prepare_content(u" ".join(
                force_text(self._resolve_field(content_obj, field_name))
                for field_name in (
                    field.name for field
                    in content_obj._meta.fields
                    if isinstance(field, (models.CharField, models.TextField))
                )
            ))
        ))

    def get_live_queryset(self):
        """Selects the live page queryset."""
        # HACK: Prevents a table name collision in the Django queryset manager.
        with publication_manager.select_published(False):
            qs = Page._base_manager.all()
        if publication_manager.select_published_active():
            qs = Page.objects.select_published(qs, page_alias="U0")
        # Filter out unindexable pages.
        qs = filter_indexable_pages(qs)
        # All done!
        return qs


# Base content class.
def get_registered_content():
    """Returns a list of all registered content objects."""
    return [
        model for model in apps.get_models()
        if issubclass(model, ContentBase) and not model._meta.abstract
    ]


def filter_indexable_pages(queryset):
    """
    Filters the given queryset of pages to only contain ones that should be
    indexed by search engines.
    """
    return [
        page.content
        for page in Page.objects.all()
        if page.content and page.content.robots_index
    ]


@python_2_unicode_compatible
class ContentBase(PageBase):

    """Base class for page content."""

    # This must be a 64 x 64 pixel image.
    icon = "pages/img/content.png"

    # The heading that the admin places this content under.
    classifier = "content"

    # The urlconf used to power this content's views.
    urlconf = "cms.apps.pages.urls"

    # A fieldset definition. If blank, one will be generated.
    fieldsets = None

    # Whether pages of this type should be included in search indexes. (Can
    # still be disabled on a per-page basis).
    robots_index = True

    page = models.ForeignKey(
        Page,
    )

    language = models.CharField(
        max_length=2,
        choices=LANGUAGES_ENGLISH,
        default=DEFAULT_LANGUAGE,
        db_index=True,
    )

    # Publication fields.
    publication_date = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        help_text="The date that this page will appear on the website.  Leave "
                  "this blank to immediately publish this page.",
    )

    expiry_date = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        help_text="The date that this page will be removed from the website.  "
                  "Leave this blank to never expire this page.",
    )

    # Navigation fields.

    in_navigation = models.BooleanField(
        "add to navigation",
        default=True,
        help_text="Uncheck this box to remove this content from the site "
                  "navigation.",
    )

    hide_from_search = models.BooleanField(
        default=False,
    )

    requires_authentication = models.BooleanField(
        default=False,
        help_text="Visitors will need to be logged in to see this page"
    )

    hide_from_anonymous = models.BooleanField(
        'show to logged in only',
        default=False,
        help_text="Visitors that aren't logged in won't see this page in the navigation"
    )

    def last_modified(self):
        if externals.reversion:
            import reversion
            versions = reversion.get_for_object(self)
            if versions.count() > 0:
                latest_version = versions[:1][0]
                return "{} by {}".format(
                    latest_version.revision.date_created.strftime("%Y-%m-%d %H:%M:%S"),
                    latest_version.revision.user
                )
        return "-"

    def get_change_url(self):
        content_type = ContentType.objects.get_for_model(type(self))
        return reverse('admin:{}_{}_change'.format(
            content_type.app_label,
            content_type.model
        ), args=[self.pk])

    def auth_required(self):
        if self.requires_authentication or not self.page.parent:
            return self.requires_authentication
        return self.page.parent.content.auth_required()

    def get_absolute_url(self):
        language = getattr(get_current_request(), 'language', 'en')

        if language is None:
            language = self.language

        # Get the ancestors for this page.
        pages = self.page.get_ancestors(ascending=False, include_self=True)

        if len(pages) == 1:
            return '/{}/'.format(language)

        return '/{}/{}/'.format(
            language,
            '/'.join([
                page.slug for page in pages[1:]
            ])
        )

    def __str__(self):
        """Returns a unicode representation."""
        return '{} - {}'.format(
            self.title,
            self.language
        )

    class Meta:
        abstract = True
