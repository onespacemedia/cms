from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, RequestFactory

from ..middleware import RequestPageManager
from ..models import ContentBase, Page
from ..templatetags.pages import get_navigation, page_url, meta_keywords, breadcrumbs
from .... import externals


class TestTemplatetagPage(ContentBase):
    urlconf = 'cms.apps.pages.tests.urls'


class TestTemplatetags(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(TestTemplatetagPage)

            self.homepage = Page.objects.create(
                title="Homepage",
                url_title='homepage',
                content_type=content_type,
            )

            TestTemplatetagPage.objects.create(
                page=self.homepage,
            )

            self.section = Page.objects.create(
                parent=self.homepage,
                title="Section",
                url_title='section',
                content_type=content_type,
            )

            TestTemplatetagPage.objects.create(
                page=self.section,
            )

            self.subsection = Page.objects.create(
                parent=self.section,
                title="Subsection",
                content_type=content_type,
            )

            TestTemplatetagPage.objects.create(
                page=self.subsection,
            )

            self.subsubsection = Page.objects.create(
                parent=self.subsection,
                title="Subsubsection",
                content_type=content_type,
            )

            TestTemplatetagPage.objects.create(
                page=self.subsubsection,
            )

    def test_get_navigation(self):
        self.homepage = Page.objects.get(pk=self.homepage.pk)
        navigation = get_navigation({'request': self.request}, self.homepage.navigation)

        self.assertListEqual(list(navigation), [
            {
                'url': '/section/',
                'page': self.section,
                'here': False,
                'title': 'Section'
            }
        ])

    def test_page_url(self):
        self.assertEqual(page_url(self.homepage), '/')
        self.assertEqual(page_url(self.homepage.pk), '/')
        self.assertEqual(page_url(-1), '#')
        self.assertEqual(page_url(None), '#')
        self.assertEqual(
            page_url(self.homepage.pk, 'detail', url_title='homepage'),
            '/homepage/'
        )

    def test_meta_keywords(self):
        self.request.pages = RequestPageManager('/', '/')

        self.assertEqual(meta_keywords({'request': self.request}), '')
        self.assertEqual(meta_keywords({
            'request': self.request,
            'meta_keywords': 'Foo'
        }), 'Foo')

    def test_breadcrumbs(self):
        class Object(object):
            current = None

        self.request.pages = Object()

        output = breadcrumbs({'request': self.request}, extended=True)
        self.assertDictEqual(output, {
            'breadcrumbs': []
        })
