from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseNotFound
from django.test import TestCase, RequestFactory

from ..middleware import RequestPageManager, PageMiddleware
from ..models import ContentBase, Page, CountryGroup, Country
from .... import externals


class TestMiddlewarePage(ContentBase):
    pass


class TestMiddlewarePageURLs(ContentBase):
    urlconf = 'cms.apps.pages.tests.urls'


def _generate_pages(self):
    with externals.watson.context_manager("update_index")():
        content_type = ContentType.objects.get_for_model(TestMiddlewarePage)

        self.homepage = Page.objects.create(
            title="Homepage",
            slug='homepage',
            content_type=content_type,
        )

        TestMiddlewarePage.objects.create(
            page=self.homepage,
        )

        self.page_1 = Page.objects.create(
            title='Foo',
            slug='foo',
            parent=self.homepage,
            content_type=content_type,
        )

        TestMiddlewarePage.objects.create(
            page=self.page_1,
        )

        self.page_2 = Page.objects.create(
            title='Bar',
            slug='bar',
            parent=self.page_1,
            content_type=content_type,
        )

        TestMiddlewarePage.objects.create(
            page=self.page_2,
        )

        self.country_group = CountryGroup.objects.create(
            name="United States of America"
        )

        self.country = Country.objects.create(
            name="United States of America",
            code="US",
            group=self.country_group
        )

        self.country_gb = Country.objects.create(
            name="United Kingdom",
            code="GB"
        )

        self.homepage_alt = Page.objects.create(
            title="Homepage",
            slug='homepage',
            owner=self.homepage,
            is_content_object=True,
            country_group=self.country_group,
            content_type=content_type,
            left=0,
            right=0,
        )

        TestMiddlewarePage.objects.create(
            page=self.homepage_alt,
        )

        self.auth_page = Page.objects.create(
            title='Auth Page',
            slug='auth',
            parent=self.homepage,
            content_type=content_type,
            requires_authentication=True,
        )

        TestMiddlewarePage.objects.create(
            page=self.auth_page,
        )


class TestRequestPageManager(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('')
        self.page_manager = RequestPageManager(self.request)

    def test_homepage(self):
        self.assertIsNone(self.page_manager.homepage)

    def test_breadcrumbs(self):
        _generate_pages(self)

        self.request = self.factory.get('/')
        page_manager = RequestPageManager(self.request)
        self.assertListEqual(page_manager.breadcrumbs, [
            self.homepage
        ])

        self.request = self.factory.get('/foo/')
        page_manager = RequestPageManager(self.request)
        self.assertListEqual(page_manager.breadcrumbs, [
            self.homepage,
            self.page_1
        ])

        self.request = self.factory.get('/foo/bar/')
        page_manager = RequestPageManager(self.request)
        self.assertListEqual(page_manager.breadcrumbs, [
            self.homepage,
            self.page_1,
            self.page_2
        ])

    def test_section(self):
        self.assertIsNone(self.page_manager.section)

        _generate_pages(self)

        self.request = self.factory.get('/foo/bar/')
        self.page_manager = RequestPageManager(self.request)
        self.assertEqual(self.page_manager.section, self.page_1)

    def test_subsection(self):
        self.assertIsNone(self.page_manager.subsection)

        _generate_pages(self)

        self.request = self.factory.get('/foo/bar/')
        self.page_manager = RequestPageManager(self.request)
        self.assertEqual(self.page_manager.subsection, self.page_2)

    def test_current(self):
        self.assertIsNone(self.page_manager.current)

        _generate_pages(self)

        self.request = self.factory.get('/foo/bar/')
        self.page_manager = RequestPageManager(self.request)
        self.assertEqual(self.page_manager.current, self.page_2)

    def test_is_exact(self):
        _generate_pages(self)
        self.page_manager._path = ''
        self.page_manager._path_info = ''
        self.assertFalse(self.page_manager.is_exact)

        self.request = self.factory.get('/foo/bar/')
        self.page_manager = RequestPageManager(self.request)
        self.assertTrue(self.page_manager.is_exact)

    def test_localisation(self):
        _generate_pages(self)

        self.assertEqual(self.country_group.__str__(), "United States of America")
        self.assertEqual(self.country.__str__(), "United States of America")

    def test_country(self):
        _generate_pages(self)

        self.request = self.factory.get('/')
        self.page_manager = RequestPageManager(self.request)
        self.assertIsNone(self.page_manager.country)

        self.request = self.factory.get('/')
        self.request.country = 'GB'
        self.page_manager = RequestPageManager(self.request)
        self.assertEqual(self.page_manager.country, 'GB')

    def test_alternate_page_version(self):
        _generate_pages(self)

        # Create a country group.
        group = CountryGroup.objects.create(
            name='Foo',
        )

        group2 = CountryGroup.objects.create(
            name='Bar',
        )

        # Create a country.
        Country.objects.create(
            code='GB',
            group=group,
        )

        country2 = Country.objects.create(
            code='FR',
            group=group2,
            default=False,
        )

        # Create an alternate version of the page with the country.
        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(TestMiddlewarePage)

            alternate_page = Page.objects.create(
                is_content_object=True,
                owner=self.homepage,
                country_group=group2,
                left=self.homepage.left,
                right=self.homepage.right,
                content_type=content_type,
            )

            TestMiddlewarePage.objects.create(
                page=alternate_page,
            )

        self.request = self.factory.get('/')
        self.request.country = country2
        self.page_manager = RequestPageManager(self.request)
        alternate_check = self.page_manager.alternate_page_version(self.homepage)

        self.assertEqual(alternate_check, alternate_page)


class MockUser(object):

    def __init__(self, authenticated=True):
        self.authenticated = authenticated

    def is_authenticated(self):
        return self.authenticated


class TestPageMiddleware(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_process_response(self):
        request = self.factory.get('/')
        response = HttpResponse()

        middleware = PageMiddleware()
        self.assertEqual(middleware.process_response(request, response), response)

        response = HttpResponseNotFound()
        page_request = self.factory.get('')
        request.pages = RequestPageManager(page_request)
        self.assertEqual(middleware.process_response(request, response), response)

        _generate_pages(self)

        request = self.factory.get('/foo/')
        request.pages = RequestPageManager(request)
        processed_response = middleware.process_response(request, response)
        self.assertEqual(processed_response.status_code, 200)
        self.assertEqual(processed_response.template_name, (
            'pages/testmiddlewarepage.html',
            'pages/base.html',
            'base.html'
        ))

        request = self.factory.get('/')
        request_foo = self.factory.get('/foo/')
        request.pages = RequestPageManager(request_foo)
        processed_response = middleware.process_response(request, response)

        self.assertEqual(processed_response['Location'], '/foo/')
        self.assertEqual(processed_response.status_code, 302)
        self.assertEqual(processed_response.content, b'')

        request = self.factory.get('/foobar/')
        request.pages = RequestPageManager(request)
        processed_response = middleware.process_response(request, response)
        self.assertEqual(processed_response.status_code, 404)

        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(TestMiddlewarePageURLs)

            self.content_url = Page.objects.create(
                title="Foo",
                slug='urls',
                parent=self.homepage,
                content_type=content_type,
            )

            TestMiddlewarePageURLs.objects.create(
                page=self.content_url,
            )

        request = self.factory.get('/urls/')
        request.pages = RequestPageManager(request)
        processed_response = middleware.process_response(request, HttpResponseNotFound())
        self.assertEqual(processed_response.status_code, 500)

        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(TestMiddlewarePageURLs)

            self.content_url = Page.objects.create(
                title="Foo",
                slug='raise404',
                parent=self.homepage,
                content_type=content_type,
            )

            TestMiddlewarePageURLs.objects.create(
                page=self.content_url,
            )

        request = self.factory.get('/raise404/')
        request.pages = RequestPageManager(request)
        processed_response = middleware.process_response(request, HttpResponseNotFound())
        self.assertEqual(processed_response.status_code, 404)

        with self.settings(DEBUG=True):
            request = self.factory.get('/raise404/')
            request.pages = RequestPageManager(request)
            processed_response = middleware.process_response(request, HttpResponseNotFound())
            self.assertEqual(processed_response.status_code, 404)

        request = self.factory.get('/auth/')
        request.user = MockUser(authenticated=False)
        request.pages = RequestPageManager(request)
        processed_response = middleware.process_response(request, response)
        self.assertEqual(processed_response['Location'], '/accounts/login/?next=/auth/')
        self.assertEqual(processed_response.status_code, 302)

        request = self.factory.get('/auth/')
        request.user = MockUser(authenticated=True)
        request.pages = RequestPageManager(request)
        processed_response = middleware.process_response(request, response)
        self.assertEqual(processed_response.status_code, 200)

        request = self.factory.get('/media/')
        request.pages = RequestPageManager(request)
        processed_response = middleware.process_response(request, response)
        self.assertEqual(processed_response, response)

        request = self.factory.get('/foo/')
        request.country = Country.objects.create(
            code='GB',
        )
        request.pages = RequestPageManager(request)
        processed_response = middleware.process_response(request, response)
        self.assertEqual(processed_response.status_code, 200)
