from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.test import RequestFactory, TestCase

from ..templatetags.permalinks import get_permalink_absolute, permalink


class TestPermalinksModel(models.Model):
    pass


class PermalinkTest(TestCase):

    def setUp(self):
        self.obj = TestPermalinksModel.objects.create()
        factory = RequestFactory()
        self.request = factory.get('/')

    def test_permalink(self):

        self.assertEqual(permalink(self.obj), '/r/{}-{}/'.format(
            ContentType.objects.get_for_model(TestPermalinksModel).pk,
            self.obj.pk
        ))

    def test_get_permalink_absolute(self):
        context = {
            'request': self.request
        }

        self.assertEqual(
            get_permalink_absolute(context, self.obj),
            'http://testserver/r/{}-{}/'.format(
                ContentType.objects.get_for_model(TestPermalinksModel).pk,
                self.obj.pk
            )
        )
