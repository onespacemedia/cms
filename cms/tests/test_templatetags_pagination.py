from django.http import Http404
from django.test import RequestFactory, TestCase

from ..templatetags.pagination import paginate, pagination, pagination_url


class Object(object):
    paginator = None


class PaginationTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

    def test_paginate(self):
        paginate_response = paginate({'request': self.request}, [])
        self.assertEqual(repr(paginate_response), '<Page 1 of 1>')

        with self.assertRaises(Http404):
            self.request = self.factory.get('/?page=2')
            paginate({'request': self.request}, [])

    def test_pagination(self):
        obj = Object()
        pagination_response = pagination({'request': self.request}, obj)

        self.assertDictEqual(pagination_response, {
            'paginator': None,
            'pagination_key': 'page',
            'page_obj': obj,
            'request': self.request,
        })

    def test_pagination_url(self):
        self.assertEqual(pagination_url({'request': self.request}, 1), '/')
        self.assertEqual(pagination_url({'request': self.request}, 2), '/?page=2')
