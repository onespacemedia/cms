from django.test import TestCase
from sorl.thumbnail.images import ImageFile

from ..templatetags.media import thumbnail


class TestTemplatetags(TestCase):

    def test_thumbnail(self):
        thumb = thumbnail('foo', '100')
        self.assertIsInstance(thumb, ImageFile)
