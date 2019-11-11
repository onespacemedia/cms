import sys

from django.conf import settings
from django.contrib import admin
from django.test import TestCase

from ..models import Country, CountryGroup, Page


class TestArticleAdminBase(TestCase):

    def test_article_admin(self):
        self.assertNotIn(Country, admin.site._registry)
        self.assertNotIn(CountryGroup, admin.site._registry)

        with self.settings(MIDDLEWARE=['cms.middleware.LocalisationMiddleware']):
            module = sys.modules['cms.apps.pages.admin']
            del sys.modules['cms.apps.pages.admin']

            admin.site.unregister(Page)

            from ..admin import page_admin
            assert page_admin

            self.assertIn(Country, admin.site._registry)
            self.assertIn(CountryGroup, admin.site._registry)

            sys.modules['cms.apps.pages.admin'] = module
