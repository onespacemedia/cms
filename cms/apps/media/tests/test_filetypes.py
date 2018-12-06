from django.test import TestCase

from ..filetypes import get_icon, get_icon_for_extension, is_image


class FiletypesTestCase(TestCase):
    def test_is_image(self):
        self.assertTrue(is_image('cms.png'))
        self.assertTrue(is_image('cms.jpg'))
        self.assertTrue(is_image('cms.jpeg'))
        self.assertTrue(is_image('cms.gif'))
        self.assertFalse(is_image('cms.pdf'))

    def test_get_icon(self):
        self.assertEqual(get_icon('cms.png'), '/static/media/img/image-x-generic.png')
        self.assertEqual(get_icon('cms.doc'), '/static/media/img/x-office-document.png')
        self.assertEqual(get_icon('cms.wat'), '/static/media/img/text-x-generic-template.png')

    def test_get_icon_for_extension(self):
        self.assertEqual(get_icon_for_extension('png'), '/static/media/img/image-x-generic.png')
        self.assertEqual(get_icon_for_extension('doc'), '/static/media/img/x-office-document.png')
        self.assertEqual(get_icon_for_extension('wat'), '/static/media/img/text-x-generic-template.png')
