from django.test import TestCase

from cms.forms import HtmlWidget
from cms.models.fields import HtmlField, LinkResolutionError, resolve_link


class TestFields(TestCase):

    def testResolveLink(self):
        self.assertEqual(resolve_link('http://www.example.com/foo/'), 'http://www.example.com/foo/')
        self.assertEqual(resolve_link('www.example.com/foo/'), 'http://www.example.com/foo/')
        self.assertEqual(resolve_link('www.example.com'), 'http://www.example.com/')
        self.assertEqual(resolve_link('/foo/'), '/foo/')
        self.assertRaises(LinkResolutionError, lambda: resolve_link('foo/'))

    def testHtmlField(self):
        field = HtmlField()
        self.assertIsInstance(field.formfield().widget, HtmlWidget)
