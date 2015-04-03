from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.test import TestCase
from django.utils.encoding import python_2_unicode_compatible

from ..templatetags.html import html, truncate_paragraphs


@python_2_unicode_compatible
class TestHTMLModel(models.Model):

    def __str__(self):
        return 'Foo'

    def get_absolute_url(self):
        return '/foo/'


class HTMLTest(TestCase):

    def test_html(self):
        self.assertEqual(html(''), '')
        self.assertEqual(html(None), 'None')
        self.assertEqual(html('Hello'), 'Hello')
        self.assertEqual(html('<span>Hello</span>'), '<span>Hello</span>')

        obj = TestHTMLModel.objects.create()
        self.assertEqual(html('<a href="/r/{}-{}/">Hello</a>'.format(
            ContentType.objects.get_for_model(TestHTMLModel).pk,
            obj.pk
        )), '<a href="/foo/" title="Foo">Hello</a>')

    def test_truncate_paragraphs(self):
        self.assertEqual(truncate_paragraphs('<p>Foo', 1), '<p>Foo')
        self.assertEqual(truncate_paragraphs('<p>Foo</p><p>Bar</p>', 0), '')
        self.assertEqual(truncate_paragraphs('<p>Foo</p><p>Bar</p>', 1), '<p>Foo</p>')
        self.assertEqual(truncate_paragraphs('<p>Foo</p><p>Bar</p>', 2), '<p>Foo</p><p>Bar</p>')
