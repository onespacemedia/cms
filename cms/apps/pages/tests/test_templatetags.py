from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, RequestFactory

from ..middleware import RequestPageManager
from ..models import ContentBase, Page, Country
from ..templatetags.pages import get_navigation, page_url, breadcrumbs, country_code
from .... import externals


class MockUser(object):
    def __init__(self, authenticated=True):
        self.authenticated = authenticated

    def is_authenticated(self):
        return self.authenticated


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
                slug='homepage',
                content_type=content_type,
            )

            TestTemplatetagPage.objects.create(
                page=self.homepage,
            )

            self.section = Page.objects.create(
                parent=self.homepage,
                title="Section",
                slug='section',
                content_type=content_type,
                hide_from_anonymous=True
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
        request = self.factory.get('/')
        request.user = MockUser(authenticated=True)
        request.pages = RequestPageManager(request)

        navigation = get_navigation({'request': request}, request.pages.current.navigation)

        self.assertListEqual(navigation, [
            {
                'url': '/section/',
                'page': self.section,
                'here': False,
                'title': 'Section'
            }
        ])

        # Section page isn't visible to non logged in users
        request.user = MockUser(authenticated=False)

        navigation = get_navigation({'request': request}, request.pages.current.navigation)

        self.assertListEqual(navigation, [])

    def test_page_url(self):
        self.assertEqual(page_url(self.homepage), '/')
        self.assertEqual(page_url(self.homepage.pk), '/')
        self.assertEqual(page_url(-1), '#')
        self.assertEqual(page_url(None), '#')
        self.assertEqual(
            page_url(self.homepage.pk, 'detail', slug='homepage'),
            '/homepage/'
        )

    def test_breadcrumbs(self):
        class Object(object):
            current = None

        self.request.pages = Object()

        output = breadcrumbs({'request': self.request}, extended=True)
        self.assertDictEqual(output, {
            'breadcrumbs': []
        })

    def test_country_code(self):
        class Context(object):
            pass

        context = Context()
        context.request = self.request
        self.assertEqual(country_code(context), '')

        country = Country.objects.create(
            code='GB',
        )

        context = Context()
        context.request = self.request
        context.request.country = country
        self.assertEqual(country_code(context), '/gb')
