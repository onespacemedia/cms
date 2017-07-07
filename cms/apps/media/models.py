"""Models used by the static media management application."""
from __future__ import unicode_literals

import os

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from PIL import Image

from tinypng.api import shrink_file


@python_2_unicode_compatible
class Label(models.Model):

    """
    A notional label used to organise static media.

    This does not correspond to a physical label on the disk.
    """

    name = models.CharField(max_length=200)

    def __str__(self):
        """Returns the name of the label."""
        return self.name

    class Meta:
        ordering = ("name",)


@python_2_unicode_compatible
class File(models.Model):

    """A static file."""

    title = models.CharField(
        max_length=200,
        help_text="The title will be used as the default rollover text when this media is embedded in a web page.",
    )

    labels = models.ManyToManyField(
        Label,
        blank=True,
        help_text='Labels are used to help organise your media. They are not visible to users on your website.',
    )

    file = models.FileField(
        upload_to='uploads/files',
        max_length=250,
    )

    width = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        default=0,
    )

    height = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        default=0,
    )

    attribution = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
    )

    copyright = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
    )

    alt_text = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )

    def get_absolute_url(self):
        """Generates the absolute URL of the image."""
        return self.file.url

    def __str__(self):
        """Returns the title of the media."""
        return self.title

    class Meta:
        ordering = ['title']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(File, self).save(force_insert, force_update, using, update_fields)
        if self.is_image():
            dimensions = self.get_dimensions()

            if dimensions:
                self.width, self.height = dimensions
                super(File, self).save(False, True, using=using, update_fields=update_fields)

        # If the file is a PNG or JPG, send it off to TinyPNG to get minified.
        if self.file and getattr(settings, 'TINYPNG_API_KEY', ''):
            _, extension = os.path.splitext(self.file.name)
            extension = extension.lower()[1:]

            if extension in ['png', 'jpg', 'jpeg']:
                try:
                    shrink_file(
                        self.file.path,
                        api_key=settings.TINYPNG_API_KEY,
                        out_filepath=self.file.path,
                    )
                # If the minification doesn't happen, that's ok.
                except:  # pylint: disable=bare-except
                    pass

    def is_image(self):
        from .admin import FILE_ICONS, IMAGE_FILE_ICON, UNKNOWN_FILE_ICON

        _, extension = os.path.splitext(self.file.name)
        extension = extension.lower()[1:]
        icon = FILE_ICONS.get(extension, UNKNOWN_FILE_ICON)
        return icon == IMAGE_FILE_ICON

    def get_dimensions(self):
        try:
            with open(self.file.path, 'rb') as f:
                try:
                    image = Image.open(f)
                    image.verify()
                except IOError:
                    return

            return image.size
        except IOError:
            return 0


class FileRefField(models.ForeignKey):

    """A foreign key to a File, constrained to only select image files."""

    def __init__(self, **kwargs):
        kwargs["to"] = 'media.File'
        kwargs.setdefault("related_name", "+")
        kwargs.setdefault("on_delete", models.PROTECT)
        super(FileRefField, self).__init__(**kwargs)

    def formfield(self, **kwargs):
        defaults = {
            "widget": ForeignKeyRawIdWidget(self.rel, admin.site),
        }
        return super(FileRefField, self).formfield(**defaults)


IMAGE_FILTER = {
    "file__iregex": r"\.(png|gif|jpg|jpeg)$"
}


class ImageRefField(FileRefField):

    """A foreign key to a File, constrained to only select image files."""

    def __init__(self, **kwargs):
        kwargs["limit_choices_to"] = IMAGE_FILTER
        super(ImageRefField, self).__init__(**kwargs)


VIDEO_FILTER = {
    "file__iregex": r"\.(webm|mp4|m4v)$"
}


class VideoFileRefField(FileRefField):

    """A foreign key to a File, constrained to only select video files."""

    def __init__(self, **kwargs):
        kwargs["limit_choices_to"] = VIDEO_FILTER
        super(VideoFileRefField, self).__init__(**kwargs)


@python_2_unicode_compatible
class Video(models.Model):

    title = models.CharField(
        max_length=200,
    )

    image = ImageRefField(
        blank=True,
        null=True,
    )

    high_resolution_mp4 = VideoFileRefField(
        verbose_name="high resolution MP4",
        blank=True,
        null=True,
    )

    low_resolution_mp4 = VideoFileRefField(
        verbose_name="low resolution MP4",
        blank=True,
        null=True
    )

    webm = VideoFileRefField(
        verbose_name="WebM",
        blank=True,
        null=True,
    )

    def __str__(self):
        """Returns the title of the media."""
        return self.title

    class Meta:
        ordering = ("title",)


class VideoRefField(models.ForeignKey):

    """A foreign key to a File, constrained to only select image files."""

    def __init__(self, **kwargs):
        kwargs["to"] = 'media.Video'
        kwargs.setdefault("related_name", "+")
        kwargs.setdefault("on_delete", models.PROTECT)
        super(VideoRefField, self).__init__(**kwargs)

    def formfield(self, **kwargs):
        defaults = {
            "widget": ForeignKeyRawIdWidget(self.rel, admin.site),
        }
        return super(VideoRefField, self).formfield(**defaults)
