"""Abstract base models used by the page management application."""
from __future__ import unicode_literals

from django.db import models
from django.shortcuts import render
from django.utils.encoding import python_2_unicode_compatible

from cms import externals
from cms.apps.media.models import ImageRefField
from cms.models.managers import OnlineBaseManager, PublishedBaseManager, SearchMetaBaseManager, PageBaseManager


class PublishedBase(models.Model):

    """A model with publication controls."""

    objects = PublishedBaseManager()

    class Meta:
        abstract = True


class PublishedBaseSearchAdapter(externals.watson.SearchAdapter):

    """Base search adapter for PublishedBase derivatives."""

    def get_live_queryset(self):
        """Selects only live models."""
        return self.model.objects.all()


class OnlineBase(PublishedBase):

    objects = OnlineBaseManager()

    is_online = models.BooleanField(
        "online",
        default=True,
        help_text=(
            "Uncheck this box to remove the page from the public website. "
            "Logged-in admin users will still be able to view this page by clicking the 'view on site' button."
        ),
    )

    class Meta:
        abstract = True


class OnlineBaseSearchAdapter(PublishedBaseSearchAdapter):

    """Base search adapter for OnlineBase derivatives."""


class SearchMetaBase(OnlineBase):

    """Base model for models used to generate a standalone HTML page."""

    objects = SearchMetaBaseManager()

    # SEO fields.

    browser_title = models.CharField(
        max_length=1000,
        blank=True,
        help_text=(
            "The heading to use in the user's web browser. "
            "Leave blank to use the page title. "
            "Search engines pay particular attention to this attribute."
        )
    )

    meta_description = models.TextField(
        "description",
        blank=True,
        help_text="A brief description of the contents of this page.",
    )

    sitemap_priority = models.FloatField(
        "priority",
        choices=(
            (1.0, "Very high"),
            (0.8, "High"),
            (0.5, "Medium"),
            (0.3, "Low"),
            (0.0, "Very low"),
        ),
        default=None,
        blank=True,
        null=True,
        help_text=(
            "The relative importance of this content in your site.  Search engines use this "
            "as a hint when ranking the pages within your site."
        ),
    )

    sitemap_changefreq = models.IntegerField(
        "change frequency",
        choices=(
            (1, "Always"),
            (2, "Hourly"),
            (3, "Daily"),
            (4, "Weekly"),
            (5, "Monthly"),
            (6, "Yearly"),
            (7, "Never")
        ),
        default=None,
        blank=True,
        null=True,
        help_text=(
            "How frequently you expect this content to be updated."
            "Search engines use this as a hint when scanning your site for updates."
        ),
    )

    robots_index = models.BooleanField(
        "allow indexing",
        default=True,
        help_text=(
            "Use this to prevent search engines from indexing this page. "
            "Disable this only if the page contains information which you do not wish "
            "to show up in search results."
        ),
    )

    robots_follow = models.BooleanField(
        "follow links",
        default=True,
        help_text=(
            "Use this to prevent search engines from following any links they find in this page. "
            "Disable this only if the page contains links to other sites that you do not wish to "
            "publicise."
        ),
    )

    robots_archive = models.BooleanField(
        "allow archiving",
        default=True,
        help_text=(
            "Use this to prevent search engines from archiving this page. "
            "Disable this only if the page is likely to change on a very regular basis. "
        ),
    )

    # Open graph fields
    og_title = models.CharField(
        verbose_name='title',
        blank=True,
        max_length=100,
        help_text='Title that will appear on the Facebook post, it is limited to 100 characters'
                  'because Facebook truncates the title to 88 characters.'
    )

    og_description = models.TextField(
        verbose_name='description',
        blank=True,
        max_length=300,
        help_text='Description that will appear ont he Facebook post, it is limited to 300'
                  'characters but is recommended not to use anything over 200.'
    )

    og_image = ImageRefField(
        verbose_name='image',
        blank=True,
        null=True,
        help_text='The recommended image size is 1200x627 (1.91/1 ratio) this gives you a big'
                  'stand out thumbnail. Using an image smaller than 400x209 will give you a very'
                  'small thumbnail and splits your post into 2 columns.'
                  ''
                  'If you have text on the image make sure it is centered as Facebook crops images'
                  'to get the text centered so you may lose some of your image.'
    )

    # Twitter card fields
    twitter_card = models.IntegerField(
        verbose_name='card',
        choices=[
            (0, 'Summary'),
            (1, 'Photo'),
            (2, 'Video'),
            (3, 'Product'),
            (4, 'App'),
            (5, 'Gallery'),
            (6, 'Large Summary'),
        ],
        blank=True,
        null=True,
        default=None,
        help_text='The type of content on the page, most of the time summary will suffice'
                  ''
                  'Before you can benefit with any of these fields make sure to go to '
                  'https://dev.twitter.com/docs/cards/validation/validator and get approved'
    )

    twitter_title = models.CharField(
        verbose_name='title',
        blank=True,
        max_length=70,
        help_text='The title that appears on the Twitter card, it is limited to 70 characters.'
    )

    twitter_description = models.TextField(
        verbose_name='description',
        blank=True,
        max_length=200,
        help_text='Description that will appear on the Twitter card, it is limited to 200 characters'
                  'You don\'t need to focus on keywords as this does\'nt effect SEO so focus on'
                  'copy that compliments the tweet and title.'
    )

    twitter_image = ImageRefField(
        verbose_name='image',
        blank=True,
        null=True,
        help_text='The minimum size it needs to be is 280x150, if you want to use a larger image'
                  'make sure the card type is set to "Large Summary"'
    )

    def get_context_data(self):
        """Returns the SEO context data for this page."""
        title = str(self)
        # Return the context.
        return {
            "meta_description": self.meta_description,
            "robots_index": self.robots_index,
            "robots_archive": self.robots_archive,
            "robots_follow": self.robots_follow,
            "title": self.browser_title or title,
            "header": title,
            "og_title": self.og_title,
            "og_description": self.og_description,
            "og_image": self.og_image,
            "twitter_card": self.twitter_card,
            "twitter_title": self.twitter_title,
            "twitter_description": self.twitter_description,
            "twitter_image": self.twitter_image
        }

    def render(self, request, template, context=None, **kwargs):
        """Renders a template as a HttpResponse using the context of this page."""
        page_context = self.get_context_data()
        page_context.update(context or {})
        return render(request, template, page_context, **kwargs)

    class Meta:
        abstract = True


class SearchMetaBaseSearchAdapter(OnlineBaseSearchAdapter):

    """Search adapter for SearchMetaBase derivatives."""

    def get_description(self, obj):
        """Returns the meta description."""
        return obj.meta_description

    def get_live_queryset(self):
        """Selects only live models."""
        return super(SearchMetaBaseSearchAdapter, self).get_live_queryset().filter(
            robots_index=True,
        )


@python_2_unicode_compatible
class PageBase(SearchMetaBase):

    """
    An enhanced SearchMetaBase with a sensible set of common features suitable for
    most pages.
    """

    objects = PageBaseManager()

    # Base fields.

    slug = models.SlugField(
        help_text='A user friendly URL'
    )

    title = models.CharField(
        max_length=1000,
    )

    # Navigation fields.

    short_title = models.CharField(
        max_length=200,
        blank=True,
        help_text=(
            "A shorter version of the title that will be used in site navigation. "
            "Leave blank to use the full-length title."
        ),
    )

    # SEO fields.

    def get_context_data(self):
        """Returns the SEO context data for this page."""
        context_data = super(PageBase, self).get_context_data()
        context_data.update({
            "title": self.browser_title or self.title,
            "header": self.title,
        })
        return context_data

    # Base model methods.

    def __str__(self):
        """
        Returns the short title of this page, falling back to the standard
        title.
        """
        return self.short_title or self.title

    class Meta:
        abstract = True


class PageBaseSearchAdapter(SearchMetaBaseSearchAdapter):

    """Search adapter for PageBase derivatives."""

    def get_title(self, obj):
        """Returns the title of the page."""
        return obj.title
