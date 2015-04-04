from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.test import TestCase
from django.utils.encoding import python_2_unicode_compatible

from ..permalinks import expand, resolve, PermalinkError


@python_2_unicode_compatible
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

        original_urlconf = urlresolvers.get_urlconf()
        with self.assertRaises(ImproperlyConfigured):
            urlresolvers.set_urlconf('cms.tests.urls')
            resolve('/r/')

        urlresolvers.set_urlconf(original_urlconf)

    def test_expand(self):
        obj = TestPermalinkModel.objects.create()

        self.assertEqual(obj.__str__(), 'Foo')

        url = expand('/r/{}-{}/'.format(
            ContentType.objects.get_for_model(TestPermalinkModel).pk,
            obj.pk
        ))

        self.assertEqual(url, '/foo/')
