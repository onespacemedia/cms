from django.db import models
from django.test import TestCase

from cms.apps.testing_models.models import (OnlineBaseModel, PageBaseModel,
                                     PublishedBaseModel, SearchMetaBaseModel,
                                     SitemapModel)
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
        register(SitemapModel)

        with self.assertRaises(SitemapRegistrationError):
            register(SitemapModel)

        self.assertEqual(
            registered_sitemaps['testing_models-sitemapmodel'].__bases__[0],
            BaseSitemap
        )

        register(SearchMetaBaseModel)

        self.assertEqual(
            registered_sitemaps['testing_models-searchmetabasemodel'].__bases__[0],
            SearchMetaBaseSitemap
        )

        register(OnlineBaseModel)

        self.assertEqual(
            registered_sitemaps['testing_models-onlinebasemodel'].__bases__[0],
            OnlineBaseSitemap
        )

        register(PublishedBaseModel)

        self.assertEqual(
            registered_sitemaps['testing_models-publishedbasemodel'].__bases__[0],
            PublishedBaseSitemap
        )

        register(PageBaseModel)

        self.assertEqual(
            registered_sitemaps['testing_models-pagebasemodel'].__bases__[0],
            PageBaseSitemap
        )
