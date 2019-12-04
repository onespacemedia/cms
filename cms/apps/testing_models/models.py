# Test-only models.
from django.db import models
from cms.apps.pages.models import ContentBase
from cms.models import OnlineBase, PageBase, PublishedBase, SearchMetaBase

from ...models.base import PublishedBaseSearchAdapter as CMSPublishedBaseSearchAdapter
from ...models.base import SearchMetaBaseSearchAdapter as CMSSearchMetaBaseSearchAdapter

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


class TestInlineModel(models.Model):
    page = models.ForeignKey(
        'pages.Page',
        on_delete=models.CASCADE,
    )


class TestInlineModelNoPage(models.Model):
    pass


class TestPageContentWithFields(ContentBase):
    description = models.TextField(
        blank=True,
    )

    inline_model = models.ManyToManyField(
        TestInlineModelNoPage,
        blank=True,
    )


class TestSitemapModel(models.Model):
    pass


class TestPageBaseModel(PageBase):
    def get_absolute_url(self):
        return '/'

class TestSearchMetaBaseModel(SearchMetaBase):
    pass


class TestOnlineBaseModel(OnlineBase):
    pass


class TestPublishedBaseModel(PublishedBase):
    pass


class TestPublishedBaseSearchAdapter(CMSPublishedBaseSearchAdapter):
    pass


class TestSearchMetaBaseSearchAdapter(CMSSearchMetaBaseSearchAdapter):
    pass
