from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from ..models.fields import resolve_link, link_validator, LinkResolutionError, LinkField


class TestFieldsModel(models.Model):

    link = LinkField()


class TestFields(TestCase):

    def test_resolve_link(self):
        with self.assertRaises(LinkResolutionError):
            resolve_link('')

        with self.assertRaises(LinkResolutionError):
            resolve_link('http://[a')

    def test_link_validator(self):
        with self.assertRaises(ValidationError):
            link_validator('')

        with self.assertRaises(ValidationError):
            link_validator('http://[a')

    def test_linkfield_get_xxx_resolved(self):
        obj = TestFieldsModel.objects.create(
            link='http://[a'
        )

        self.assertEqual(obj.get_link_resolved(), 'http://[a')
