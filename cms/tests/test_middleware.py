from django.template.response import SimpleTemplateResponse
from django.test import TestCase, RequestFactory


from ..middleware import PublicationMiddleware


class MiddlewareTest(TestCase):

    def setUp(self):
        factory = RequestFactory()
        self.request = factory.get('/?preview=a')

    def test_publicationmiddleware_process_request(self):
        publication_middleware = PublicationMiddleware()
        publication_middleware.process_request(self.request)

    def test_publicationmiddleware_process_response(self):
        response = SimpleTemplateResponse('../templates/pagination/pagination.html')
        publication_middleware = PublicationMiddleware()

        response = publication_middleware.process_response(self.request, response)

        self.assertEqual(response.status_code, 200)
