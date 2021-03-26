"""Abstract base models used by the page management application."""
from django.db import models
from django.shortcuts import render
from django.utils.crypto import constant_time_compare, salted_hmac
from watson.search import SearchAdapter

from cms.apps.media.models import ImageRefField
from cms.models.managers import (OnlineBaseManager, PageBaseManager,
                                 PublishedBaseManager, SearchMetaBaseManager)


class PathTokenGenerator:
    '''
        A simple token generator that takes a path and generates a hash for it.
        Intended for use by the CMS publication middleware and OnlineBase derivatives.
        In reality it just takes a string so it can be used for other purposes.
    '''
    key_salt = "django.contrib.auth.tokens.PasswordResetTokenGenerator"

    def make_token(self, path):
        return salted_hmac(
            self.key_salt,
            path,
        ).hexdigest()[::2]

    def check_token(self, token, path):
        return constant_time_compare(
            token,
            salted_hmac(self.key_salt, path).hexdigest()[::2]
        )

path_token_generator = PathTokenGenerator()


class PublishedBase(models.Model):

    """A model with publication controls."""

    objects = PublishedBaseManager()

    class Meta:
        abstract = True


class PublishedBaseSearchAdapter(SearchAdapter):

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

    def get_preview_url(self):
        if not hasattr(self, 'get_absolute_url'):
            return None

        return f'{self.get_absolute_url()}?preview={path_token_generator.make_token(self.get_absolute_url())}'

    class Meta:
        abstract = True


class OnlineBaseSearchAdapter(PublishedBaseSearchAdapter):

    """Base search adapter for OnlineBase derivatives."""


class SearchMetaBase(OnlineBase):

    """Base model for models used to generate a standalone HTML page."""

    objects = SearchMetaBaseManager()

    # SEO fields.

    browser_title = models.CharField(
        "Title tag",
        max_length=1000,
        blank=True,
        help_text=(
            "The title that appears in search results. Use 50-60 characters and include relevant keywords."
        )
    )

    meta_description = models.TextField(
        blank=True,
        help_text="A concise and compelling description of the contents of the page. Use 50-160 characters and include relevant keywords.",
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
            "The relative importance of this content on your site. Search engines use this "
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
            "How frequently you expect this content to be updated. "
            "Search engines use this as a hint when scanning your site for updates."
        ),
    )

    robots_index = models.BooleanField(
        "allow indexing",
        default=True,
        help_text=(
            "Uncheck to prevent search engines from indexing this page. "
            "Do this only if the page contains information which you do not wish "
            "to show up in search results."
        ),
    )

    robots_follow = models.BooleanField(
        "follow links",
        default=True,
        help_text=(
            "Uncheck to prevent search engines from following any links they find in this page. "
            "Do this only if the page contains links to other sites that you do not wish to "
            "publicise."
        ),
    )

    robots_archive = models.BooleanField(
        "allow archiving",
        default=True,
        help_text=(
            "Uncheck this to prevent search engines from archiving this page. "
            "Do this this only if the page is likely to change on a very regular basis. "
        ),
    )

    # Open Graph fields
    og_title = models.CharField(
        verbose_name='title',
        blank=True,
        max_length=100,
        help_text='Title that will appear on social media posts. This is limited to 100 characters, '
                  'but Facebook will truncate the title to 88 characters.'
    )

    og_description = models.TextField(
        verbose_name='description',
        blank=True,
        max_length=300,
        help_text='Description that will appear on social media posts. It is limited to 300 '
                  'characters, but it is recommended that you do not use anything over 200.'
    )

    og_image = ImageRefField(
        verbose_name='image',
        blank=True,
        null=True,
        help_text='The recommended image size is 1200x627 (1.91:1 ratio); this gives you a big '
                  'stand out thumbnail. Using an image smaller than 400x209 will give you a '
                  'small thumbnail and will splits posts into 2 columns. '
                  'If you have text on the image make sure it is centered.'
    )

    # Twitter card fields
    # If you make a change here, you'll also need to update the lookup dict in
    # pages/templatetages/pages.py where used.
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
        help_text='The type of content on the page. Most of the time "Summary" will suffice. '
                  'Before you can benefit from any of these fields make sure to go to '
                  'https://dev.twitter.com/docs/cards/validation/validator and get approved.'
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
        help_text='Description that will appear on Twitter cards. It is limited '
                  'to 200 characters. This does\'nt effect SEO, so focus on copy '
                  'that complements the tweet and title rather than on keywords.'
    )

    twitter_image = ImageRefField(
        verbose_name='image',
        blank=True,
        null=True,
        help_text='The minimum size it needs to be is 280x150. If you want to use a larger image'
                  'make sure the card type is set to "Large Summary".'
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
        return super().get_live_queryset().filter(robots_index=True)


class PageBase(SearchMetaBase):

    """
    An enhanced SearchMetaBase with a sensible set of common features suitable for
    most pages.
    """

    objects = PageBaseManager()

    # Base fields.

    slug = models.SlugField(
        max_length=150,
        help_text='A unique portion of the URL that is used to identify this '
                  'specific page using human-readable keywords (e.g., about-us)'
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
        context_data = super().get_context_data()
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
