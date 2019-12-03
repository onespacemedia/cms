# Test-only models.
from django.db import models
from cms.apps.pages.models import ContentBase
from cms.models import OnlineBase, PageBase, PublishedBase, SearchMetaBase


class TestPageContent(ContentBase):
    urlconf = 'cms.apps.pages.tests.urls'


class TestPageContentWithSections(ContentBase):
    testing = models.CharField(
        max_length=20,
        default='testing',
    )


class TestSection(models.Model):

    page = models.ForeignKey(
        'pages.Page',
        on_delete=models.CASCADE,
    )

    title = models.CharField(
        max_length=100,
    )


class InlineModel(models.Model):
    page = models.ForeignKey(
        'pages.Page',
        on_delete=models.CASCADE,
    )


class InlineModelNoPage(models.Model):
    pass


class TestPageContentWithFields(ContentBase):
    description = models.TextField(
        blank=True,
    )

    inline_model = models.ManyToManyField(
        InlineModelNoPage,
        blank=True,
    )


class SitemapModel(models.Model):
    pass


class PageBaseModel(PageBase):
    pass


class SearchMetaBaseModel(SearchMetaBase):
    pass


class OnlineBaseModel(OnlineBase):
    pass


class PublishedBaseModel(PublishedBase):
    pass
