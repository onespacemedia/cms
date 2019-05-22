from django.http import Http404
from django.test import RequestFactory, TestCase

from ..templatetags.pagination import (get_pagination_url, paginate,
                                       render_pagination)


class Object:
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
        obj.has_other_pages = lambda: False
        pagination_response = render_pagination({'request': self.request}, obj)

        self.assertTrue(len(pagination_response) == 0)

        obj.has_other_pages = lambda: True
        obj.has_previous = lambda: False
        obj.has_next = lambda: False
        obj.paginator = Object()
        obj.paginator.page_range = []
        pagination_response = render_pagination({'request': self.request}, obj)

        self.assertTrue(len(pagination_response) > 0)

    def test_pagination_url(self):
        self.assertEqual(get_pagination_url({'request': self.request}, 1), '/')
        self.assertEqual(get_pagination_url({'request': self.request}, 2), '/?page=2')
