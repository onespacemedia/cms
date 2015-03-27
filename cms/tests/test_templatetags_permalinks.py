from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.test import RequestFactory, TestCase

from ..templatetags.permalinks import permalink, permalink_absolute


class TestModel(models.Model):
    pass


class PermalinkTest(TestCase):

    def setUp(self):
        self.obj = TestModel.objects.create()
        factory = RequestFactory()
        self.request = factory.get('/')

    def test_permalink(self):

        self.assertEqual(permalink(self.obj), '/r/{}-{}/'.format(
            ContentType.objects.get_for_model(TestModel).pk,
            self.obj.pk
        ))

    def test_permalink_absolute(self):
        context = {
            'request': self.request
        }

        self.assertEqual(permalink_absolute(context, self.obj), 'http://testserver/r/{}-{}/'.format(
            ContentType.objects.get_for_model(TestModel).pk,
            self.obj.pk
        ))
