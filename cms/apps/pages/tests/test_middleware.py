from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.test import TestCase, RequestFactory

from ..middleware import RequestPageManager, PageMiddleware
from ..models import ContentBase, Page
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
            url_title='homepage',
            content_type=content_type,
        )

        TestMiddlewarePage.objects.create(
            page=self.homepage,
        )

        self.page_1 = Page.objects.create(
            title='Foo',
            url_title='foo',
            parent=self.homepage,
            content_type=content_type,
        )

        TestMiddlewarePage.objects.create(
            page=self.page_1,
        )

        self.page_2 = Page.objects.create(
            title='Bar',
            url_title='bar',
            parent=self.page_1,
            content_type=content_type,
        )

        TestMiddlewarePage.objects.create(
            page=self.page_2,
        )


class TestRequestPageManager(TestCase):

    def setUp(self):
        self.page_manager = RequestPageManager('', '')

    def test_homepage(self):
        self.assertIsNone(self.page_manager.homepage)

    def test_breadcrumbs(self):
        _generate_pages(self)

        page_manager = RequestPageManager('', '/')
        self.assertListEqual(page_manager.breadcrumbs, [
            self.homepage
        ])

        page_manager = RequestPageManager('', '/foo/')
        self.assertListEqual(page_manager.breadcrumbs, [
            self.homepage,
            self.page_1
        ])

        page_manager = RequestPageManager('', '/foo/bar/')
        self.assertListEqual(page_manager.breadcrumbs, [
            self.homepage,
            self.page_1,
            self.page_2
        ])

    def test_section(self):
        self.assertIsNone(self.page_manager.section)

        _generate_pages(self)

        self.page_manager = RequestPageManager('', '/foo/bar/')
        self.assertEqual(self.page_manager.section, self.page_1)

    def test_subsection(self):
        self.assertIsNone(self.page_manager.subsection)

        _generate_pages(self)

        self.page_manager = RequestPageManager('', '/foo/bar/')
        self.assertEqual(self.page_manager.subsection, self.page_2)

    def test_current(self):
        self.assertIsNone(self.page_manager.current)

        _generate_pages(self)

        self.page_manager = RequestPageManager('', '/foo/bar/')
        self.assertEqual(self.page_manager.current, self.page_2)

    def test_is_exact(self):
        _generate_pages(self)
        self.assertFalse(self.page_manager.is_exact)

        self.page_manager = RequestPageManager('/foo/bar/', '/foo/bar/')
        self.assertTrue(self.page_manager.is_exact)


class TestPageMiddleware(TestCase):

    def test_process_response(self):
        factory = RequestFactory()
        request = factory.get('/')
        response = HttpResponse()

        middleware = PageMiddleware()
        self.assertEqual(middleware.process_response(request, response), response)

        response = HttpResponseNotFound()
        request.pages = RequestPageManager('', '')
        self.assertEqual(middleware.process_response(request, response), response)

        _generate_pages(self)

        request = factory.get('/foo/')
        request.pages = RequestPageManager('/foo/', '/foo/')
        processed_response = middleware.process_response(request, response)
        self.assertEqual(processed_response.status_code, 200)
        self.assertEqual(processed_response.template_name, (
            'pages/testmiddlewarepage.html',
            'pages/base.html',
            'base.html'
        ))

        request = factory.get('/')
        request.pages = RequestPageManager('/foo/', '/foo/')
        processed_response = middleware.process_response(request, response)

        self.assertEqual(processed_response['Location'], '/foo/')
        self.assertEqual(processed_response.status_code, 302)
        self.assertEqual(processed_response.content, b'')

        request = factory.get('/foobar/')
        request.pages = RequestPageManager('/foobar/', '/foobar/')
        processed_response = middleware.process_response(request, response)
        self.assertEqual(processed_response.status_code, 404)

        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(TestMiddlewarePageURLs)

            self.content_url = Page.objects.create(
                title="Foo",
                url_title='urls',
                parent=self.homepage,
                content_type=content_type,
            )

            TestMiddlewarePageURLs.objects.create(
                page=self.content_url,
            )

        request = factory.get('/urls/')
        request.pages = RequestPageManager('/urls/', '/urls/')
        processed_response = middleware.process_response(request, HttpResponseNotFound())
        self.assertEqual(processed_response.status_code, 500)

        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(TestMiddlewarePageURLs)

            self.content_url = Page.objects.create(
                title="Foo",
                url_title='raise404',
                parent=self.homepage,
                content_type=content_type,
            )

            TestMiddlewarePageURLs.objects.create(
                page=self.content_url,
            )

        request = factory.get('/raise404/')
        request.pages = RequestPageManager('/raise404/', '/raise404/')
        processed_response = middleware.process_response(request, HttpResponseNotFound())
        self.assertEqual(processed_response.status_code, 404)

        with self.settings(DEBUG=True):
            request = factory.get('/raise404/')
            request.pages = RequestPageManager('/raise404/', '/raise404/')
            processed_response = middleware.process_response(request, HttpResponseNotFound())
            self.assertEqual(processed_response.status_code, 404)
