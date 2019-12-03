import os

from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.template.response import SimpleTemplateResponse
from django.test import RequestFactory, TestCase
from watson import search

from ..apps.pages.models import ContentBase, Country, Page
from ..middleware import LocalisationMiddleware, PublicationMiddleware


class TestContentBase(ContentBase):
    pass


class MiddlewareTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/?preview=a')
        self.request.user = AnonymousUser()

    def test_publicationmiddleware_process_request(self):
        publication_middleware = PublicationMiddleware()
        publication_middleware.process_request(self.request)

    def test_publicationmiddleware_process_response(self):
        class Context(dict):
            pass

        context = Context()
        context['page_obj'] = Context()
        context['page_obj'].has_other_pages = lambda: False

        response = SimpleTemplateResponse('pagination/pagination.html', context)
        publication_middleware = PublicationMiddleware()

        response = publication_middleware.process_response(self.request, response)

        self.assertEqual(response.status_code, 200)

    def test_publicationmiddleware_preview(self):
        with search.update_index():
            page_obj = Page.objects.create(
                title='Foo',
                content_type=ContentType.objects.get_for_model(TestContentBase),
                is_online=False,
            )

            content_obj = TestContentBase.objects.create(page=page_obj)

        middleware = [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'cms.middleware.PublicationMiddleware',
            'cms.apps.pages.middleware.PageMiddleware',
        ]

        with self.settings(MIDDLEWARE=middleware):
            request = self.client.get(page_obj.get_absolute_url())
            self.assertEqual(request.status_code, 404)

            # Ensure preview mode (without a valid token) fails for
            # non-authenticated users.
            request = self.client.get(page_obj.get_absolute_url() + '?preview=1')
            self.assertEqual(request.status_code, 404)

            request = self.client.get(page_obj.get_preview_url())
            self.assertEqual(request.status_code, 200)

    def test_localisationmiddleware_process_request(self):
        localisation_middleware = LocalisationMiddleware()

        self.request = self.factory.get('/media/')
        self.assertIsNone(localisation_middleware.process_request(self.request))

        self.request = self.factory.get('/admin/')
        self.assertIsNone(localisation_middleware.process_request(self.request))

        self.request = self.factory.get('/social-auth/')
        self.assertIsNone(localisation_middleware.process_request(self.request))

        self.request = self.factory.get('/gb/')
        self.assertIsNone(localisation_middleware.process_request(self.request))

        self.assertEqual(self.request.path_info, '/gb/')
        self.assertEqual(self.request.path, '/gb/')
        self.assertIsNone(self.request.country)

        # Add a country.
        obj = Country.objects.create(
            code='GB'
        )
        self.assertIsNone(localisation_middleware.process_request(self.request))
        self.assertEqual(self.request.path_info, '/')
        self.assertEqual(self.request.path, '/')
        self.assertEqual(self.request.country, obj)

    def test_localisationmiddleware_process_request_lowercase(self):
        localisation_middleware = LocalisationMiddleware()

        # Add a country.
        obj = Country.objects.create(
            code='gb'
        )

        self.request = self.factory.get('/gb/')
        self.assertIsNone(localisation_middleware.process_request(self.request))
        self.assertEqual(self.request.path_info, '/')
        self.assertEqual(self.request.path, '/')
        self.assertEqual(self.request.country, obj)

    def test_localisationmiddleware_process_response(self):
        import geoip2

        class Context(dict):
            pass

        context = Context()
        context['page_obj'] = Context()
        context['page_obj'].has_other_pages = lambda: False

        response = SimpleTemplateResponse('pagination/pagination.html', context)
        localisation_middleware = LocalisationMiddleware()

        geoip_dat_file = '{}/geolite2/GeoLite2-Country.mmdb'.format(os.path.dirname(os.path.realpath(__file__)))

        self.request = self.factory.get('/media/')
        processed_response = localisation_middleware.process_response(self.request, response, geoip_path=geoip_dat_file)
        self.assertEqual(processed_response, response)
        self.assertEqual(processed_response.status_code, 200)

        obj = Country.objects.create(
            code='GB',
        )

        self.request = self.factory.get('/')
        localisation_middleware.process_request(self.request)

        try:
            processed_response = localisation_middleware.process_response(self.request, response, geoip_path=geoip_dat_file)
        except geoip2.errors.AddressNotFoundError:
            self.request.country = obj
            processed_response = localisation_middleware.process_response(self.request, response, geoip_path=geoip_dat_file)

        self.assertEqual(processed_response, response)

        # Give ourselves a direct IP.
        self.request = self.factory.get('/')
        self.request.META['REMOTE_ADDR'] = '212.58.246.103'
        localisation_middleware.process_request(self.request)
        processed_response = localisation_middleware.process_response(self.request, response, geoip_path=geoip_dat_file)

        self.assertEqual(processed_response.status_code, 302)
        self.assertNotEqual(processed_response, response)
        self.assertEqual(self.request.country, obj)

        # Give ourselves a proxied IP.
        self.request = self.factory.get('/')
        self.request.META['HTTP_X_FORWARDED_FOR'] = '212.58.246.103'
        localisation_middleware.process_request(self.request)
        processed_response = localisation_middleware.process_response(self.request, response, geoip_path=geoip_dat_file)

        self.assertEqual(processed_response.status_code, 302)
        self.assertNotEqual(processed_response, response)
        self.assertEqual(self.request.country, obj)

        # Give ourselves a French IP.
        self.request = self.factory.get('/')
        self.request.META['REMOTE_ADDR'] = '2.15.255.255'
        localisation_middleware.process_request(self.request)
        processed_response = localisation_middleware.process_response(self.request, response, geoip_path=geoip_dat_file)

        self.assertEqual(processed_response.status_code, 200)
        self.assertEqual(processed_response, response)
        self.assertIsNone(self.request.country)

        obj = Country.objects.create(
            code='US',
        )

        self.request = self.factory.get('/')
        # Give ourselves a US West IP.
        self.request.META['REMOTE_ADDR'] = '52.52.95.213'
        localisation_middleware.process_request(self.request)
        processed_response = localisation_middleware.process_response(self.request, response, geoip_path=geoip_dat_file)

        self.assertEqual(processed_response.status_code, 302)
        self.assertNotEqual(processed_response, response)
        self.assertEqual(self.request.country, obj)

        obj = Country.objects.create(
            code='IN',
        )

        self.request = self.factory.get('/')

        # Give ourselves an Indian IP.
        self.request.META['REMOTE_ADDR'] = '13.232.220.164'
        localisation_middleware.process_request(self.request)
        processed_response = localisation_middleware.process_response(self.request, response, geoip_path=geoip_dat_file)

        self.assertEqual(processed_response.status_code, 302)
        self.assertNotEqual(processed_response, response)
        self.assertEqual(self.request.country, obj)

        # Give ourselves a Japanese IP
        self.request.META['REMOTE_ADDR'] = '52.194.115.181'
        localisation_middleware.process_request(self.request)
        processed_response = localisation_middleware.process_response(self.request, response, geoip_path=geoip_dat_file)

        # Test Indian country code with Japanese IP
        self.assertNotEqual(self.request.country, obj)
