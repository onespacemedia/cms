from django.db import models
from django.test import TestCase

from ..models import SearchMetaBase, OnlineBase, PublishedBase
from ..sitemaps import (BaseSitemap, SearchMetaBaseSitemap, OnlineBaseSitemap,
                        PublishedBaseSitemap, SitemapRegistrationError,
                        register, registered_sitemaps)


class SitemapModel(models.Model):
    pass


class SearchMetaBaseModel(SearchMetaBase):
    pass


class OnlineBaseModel(OnlineBase):
    pass


class PublishedBaseModel(PublishedBase):
    pass


class Object(object):

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
            registered_sitemaps['cms-sitemapmodel'].__bases__[0],
            BaseSitemap
        )

        register(SearchMetaBaseModel)

        self.assertEqual(
            registered_sitemaps['cms-searchmetabasemodel'].__bases__[0],
            SearchMetaBaseSitemap
        )

        register(OnlineBaseModel)

        self.assertEqual(
            registered_sitemaps['cms-onlinebasemodel'].__bases__[0],
            OnlineBaseSitemap
        )

        register(PublishedBaseModel)

        self.assertEqual(
            registered_sitemaps['cms-publishedbasemodel'].__bases__[0],
            PublishedBaseSitemap
        )
