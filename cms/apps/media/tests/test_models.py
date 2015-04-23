from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.test import TestCase
from django.utils import six
from django.utils.timezone import now

from ..models import File, FileRefField, Label, Video, VideoFileRefField, VideoRefField

import base64
import random


class TestModel(models.Model):

    file = FileRefField(
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    video_file = VideoFileRefField(
        blank=True,
        null=True,
    )

    video = VideoRefField(
        blank=True,
        null=True,
    )


class TestLabel(TestCase):

    def test_label_unicode(self):
        obj = Label.objects.create(
            name="Foo"
        )

        self.assertEqual(repr(obj), "<Label: Foo>")
        self.assertEqual(str(obj), "Foo")
        self.assertEqual(obj.__str__(), "Foo")


class TestFile(TestCase):

    def setUp(self):
        # An invalid JPEG
        self.name_1 = '{}-{}.jpg'.format(
            now().strftime('%Y-%m-%d_%H-%M-%S'),
            random.randint(0, six.MAXSIZE)
        )

        self.obj_1 = File.objects.create(
            title="Foo",
            file=SimpleUploadedFile(self.name_1, b"data", content_type="image/jpeg")
        )

        # Plain text file
        self.name_2 = '{}-{}.txt'.format(
            now().strftime('%Y-%m-%d_%H-%M-%S'),
            random.randint(0, six.MAXSIZE)
        )

        self.obj_2 = File.objects.create(
            title="Foo",
            file=SimpleUploadedFile(self.name_2, b"data", content_type="text/plain")
        )

        # A valid GIF.
        self.name_3 = '{}-{}.gif'.format(
            now().strftime('%Y-%m-%d_%H-%M-%S'),
            random.randint(0, six.MAXSIZE)
        )

        base64_string = b'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
        self.obj_3 = File.objects.create(
            title="Foo",
            file=SimpleUploadedFile(self.name_3, base64.b64decode(base64_string), content_type="image/gif")
        )

    def tearDown(self):
        self.obj_1.file.delete(False)
        self.obj_1.delete()

        self.obj_2.file.delete(False)
        self.obj_2.delete()

        self.obj_3.file.delete(False)
        self.obj_3.delete()

    def test_file_get_absolute_url(self):
        self.assertEqual(self.obj_1.get_absolute_url(), '/media/uploads/files/{}'.format(
            self.name_1
        ))

    def test_file_unicode(self):
        self.assertEqual(self.obj_1.__str__(), 'Foo')
        self.assertEqual(self.obj_1.file.name, 'uploads/files/' + self.name_1)

    def test_file_is_image(self):
        self.assertTrue(self.obj_1.is_image())
        self.assertFalse(self.obj_2.is_image())

    def test_file_width(self):
        self.assertEqual(self.obj_1.width(), 0)
        self.assertEqual(self.obj_2.width(), 0)
        self.assertEqual(self.obj_3.width(), 1)

    def test_file_height(self):
        self.assertEqual(self.obj_1.height(), 0)
        self.assertEqual(self.obj_2.height(), 0)
        self.assertEqual(self.obj_3.height(), 1)

    def test_filereffield_formfield(self):
        obj = TestModel.objects.create(
            file=self.obj_1
        )

        field = obj._meta.get_field('file')
        widget = field.formfield().widget

        self.assertIsInstance(widget, ForeignKeyRawIdWidget)
        self.assertEqual(widget.rel, field.rel)
        self.assertEqual(widget.admin_site, admin.site)
        self.assertIsNone(widget.db)

    def test_file_init(self):
        field = FileRefField(
            to=TestModel,
        )

        self.assertEqual(field.rel.to, 'media.File')


class TestVideo(TestCase):

    def setUp(self):
        # An invalid JPEG
        self.name_1 = '{}-{}.jpg'.format(
            now().strftime('%Y-%m-%d_%H-%M-%S'),
            random.randint(0, six.MAXSIZE)
        )

        self.obj_1 = File.objects.create(
            title="Foo",
            file=SimpleUploadedFile(self.name_1, b"data", content_type="image/jpeg")
        )

    def test_videofilereffield_init(self):
        obj = TestModel.objects.create(
            video_file=self.obj_1
        )

        self.assertEqual(
            obj._meta.get_field('video_file').get_limit_choices_to(),
            {'file__iregex': '\\.(webm|mp4|m4v)$'}
        )

    def test_videoreffield_init(self):
        video = Video.objects.create(
            title='Foo',
            high_resolution_mp4=self.obj_1
        )

        obj = TestModel.objects.create(
            video=video
        )

        field = obj._meta.get_field('video')
        rel = obj._meta.get_field('video').rel

        self.assertEqual(rel.to, Video)
        self.assertEqual(rel.related_name, '+')
        self.assertEqual(rel.on_delete, models.PROTECT)

        widget = field.formfield().widget
        self.assertIsInstance(widget, ForeignKeyRawIdWidget)
        self.assertEqual(widget.rel, field.rel)
        self.assertEqual(widget.admin_site, admin.site)
        self.assertIsNone(widget.db)

    def test_video_unicode(self):
        video = Video.objects.create(
            title='Foo',
            high_resolution_mp4=self.obj_1
        )

        self.assertEqual(video.__str__(), 'Foo')
