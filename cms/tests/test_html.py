import base64
import random
import re

from unittest import mock
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import six
from django.utils.timezone import now

from ..apps.media.models import File
from ..html import process


class TestHTML(TestCase):
    def setUp(self):
        self.name = '{}-{}.gif'.format(
            now().strftime('%Y-%m-%d_%H-%M-%S'),
            random.randint(0, six.MAXSIZE)
        )

        base64_string = b'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
        self.image = File.objects.create(
            title="Foo",
            file=SimpleUploadedFile(self.name, base64.b64decode(base64_string),
                                    content_type="image/gif")
        )

        self.image_copyright = File.objects.create(
            title="Foo c",
            file=SimpleUploadedFile(self.name, base64.b64decode(base64_string),
                                    content_type="image/gif"),
            copyright="Foo copyright"
        )

        self.image_attribution = File.objects.create(
            title="Foo a",
            file=SimpleUploadedFile(self.name, base64.b64decode(base64_string),
                                    content_type="image/gif"),
            attribution="Foo attribution"
        )

        # An invalid JPEG
        self.invalid_jpeg_name = '{}-{}.jpg'.format(
            now().strftime('%Y-%m-%d_%H-%M-%S'),
            random.randint(0, six.MAXSIZE)
        )

        self.invalid_jpeg = File.objects.create(
            title="Foo",
            file=SimpleUploadedFile(self.invalid_jpeg_name, b"data",
                                    content_type="image/jpeg")
        )

    def tearDown(self):
        self.image.file.delete(False)
        self.image.delete()

        self.image_copyright.file.delete(False)
        self.image_copyright.delete()

        self.image_attribution.file.delete(False)
        self.image_attribution.delete()

        self.invalid_jpeg.file.delete(False)
        self.invalid_jpeg.delete()

    def test_process(self):
        string = ''
        self.assertEqual(process(string), string)

        string = '<a href="/">Link</a>'
        self.assertEqual(process(string), string)

        string = '<img src="test.png"/>'
        self.assertEqual(process(string), string)

        string = '<img src="test.png"/>'
        self.assertEqual(process(string), string)

        string = '<img />'
        self.assertEqual(process(string), string)

        content_type = ContentType.objects.get_for_model(File).pk
        string = '<img src="/r/{}-{}/" width="10" height="10"/>'.format(
            content_type,
            self.image.pk
        )
        output = process(string)

        self.assertIn('src="/media/cache/', output)
        self.assertIn('height="10"', output)
        self.assertIn('width="10"', output)
        self.assertIn('title="Foo"', output)

        with mock.patch('cms.html.get_thumbnail', side_effect=IOError):
            output = process(string)

        self.assertEqual(output,
                         '<img height="10" src="/media/uploads/files/' + self.name + '" title="Foo" width="10"/>')

        content_type = ContentType.objects.get_for_model(File).pk
        string = '<img src="/r/{}-{}/"/>'.format(
            content_type,
            self.image.pk
        )
        self.assertEqual(process(string),
                         '<img src="' + self.image.file.url + '" title="Foo"/>')

        string = '<img src="/r/{}-{}/"/>'.format(
            content_type,
            self.image_copyright.pk
        )
        self.assertEqual(process(string),
                         '<img src="' + self.image_copyright.file.url + '" title="&copy; Foo copyright. "/>')

        string = '<img src="/r/{}-{}/"/>'.format(
            content_type,
            self.image_attribution.pk
        )
        self.assertEqual(process(string),
                         '<img src="' + self.image_attribution.file.url + '" title="Foo attribution"/>')

        re_tag = re.compile(r"<(img|ab)(\s+.*?)(/?)>", re.IGNORECASE)
        with mock.patch('cms.html.RE_TAG', new=re_tag), \
                self.assertRaises(AssertionError):
            process('<ab />')
