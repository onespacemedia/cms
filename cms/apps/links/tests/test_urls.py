from django.test import TestCase

from ..urls import urlpatterns


class TestURLs(TestCase):

    def test_urlpatterns(self):
        self.assertEqual(len(urlpatterns), 1)
