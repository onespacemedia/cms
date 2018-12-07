from django import urls
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.test import TestCase

from ..permalinks import PermalinkError, expand, resolve


class TestPermalinkModel(models.Model):

    def __str__(self):
        return 'Foo'

    def get_absolute_url(self):
        return '/foo/'


class PermalinksTest(TestCase):

    def test_resolve(self):
        obj = TestPermalinkModel.objects.create()

        url = resolve('/r/{}-{}/'.format(
            ContentType.objects.get_for_model(TestPermalinkModel).pk,
            obj.pk
        ))

        self.assertEqual(url, obj)

        with self.assertRaises(PermalinkError):
            # A valid URL, but not a permalink.
            resolve('/admin/')

        original_urlconf = urls.get_urlconf()
        with self.assertRaises(PermalinkError):
            urls.set_urlconf('cms.tests.urls')
            resolve('/r/')

        urls.set_urlconf(original_urlconf)

    def test_expand(self):
        obj = TestPermalinkModel.objects.create()

        self.assertEqual(obj.__str__(), 'Foo')

        url = expand('/r/{}-{}/'.format(
            ContentType.objects.get_for_model(TestPermalinkModel).pk,
            obj.pk
        ))

        self.assertEqual(url, '/foo/')
