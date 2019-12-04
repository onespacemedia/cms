from django.db import models
from django.test import TestCase

from cms.apps.testing_models.models import (TestOnlineBaseModel, TestPageBaseModel,
                                     TestPublishedBaseModel, TestSearchMetaBaseModel,
                                     TestSitemapModel)
from cms.sitemaps import (BaseSitemap, OnlineBaseSitemap, PageBaseSitemap,
                          PublishedBaseSitemap, SearchMetaBaseSitemap,
                          SitemapRegistrationError, register,
                          registered_sitemaps)


class Object:

    sitemap_priority = 1

    def __init__(self, *args, **kwargs):
        self.sitemap_changefreq = kwargs.get('freq', 1)

    def get_sitemap_changefreq_display(self):
        return 'Always'


class TestSitemaps(TestCase):

    def test_searchmetabasesitemap_changefreq(self):
        sitemap = SearchMetaBaseSitemap()
        obj = Object()
        self.assertEqual(sitemap.changefreq(obj), 'always')

        obj = Object(freq=None)
        self.assertIsNone(sitemap.changefreq(obj))

    def test_searchmetabasesitemap_priority(self):
        sitemap = SearchMetaBaseSitemap()
        obj = Object()
        self.assertEqual(sitemap.priority(obj), 1)

    def test_register(self):
        register(TestSitemapModel)

        with self.assertRaises(SitemapRegistrationError):
            register(TestSitemapModel)

        self.assertEqual(
            registered_sitemaps['testing_models-testsitemapmodel'].__bases__[0],
            BaseSitemap
        )

        register(TestSearchMetaBaseModel)

        self.assertEqual(
            registered_sitemaps['testing_models-testsearchmetabasemodel'].__bases__[0],
            SearchMetaBaseSitemap
        )

        register(TestOnlineBaseModel)

        self.assertEqual(
            registered_sitemaps['testing_models-testonlinebasemodel'].__bases__[0],
            OnlineBaseSitemap
        )

        register(TestPublishedBaseModel)

        self.assertEqual(
            registered_sitemaps['testing_models-testpublishedbasemodel'].__bases__[0],
            PublishedBaseSitemap
        )

        register(TestPageBaseModel)

        self.assertEqual(
            registered_sitemaps['testing_models-testpagebasemodel'].__bases__[0],
            PageBaseSitemap
        )
