"""Models used by the static media management application."""

from django.db import models
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget

import os


class Label(models.Model):

    """
    A notional label used to organise static media.

    This does not correspond to a physical label on the disk.
    """

    name = models.CharField(max_length=200)

    def __unicode__(self):
        """Returns the name of the label."""
        return self.name

    class Meta:
        ordering = ("name",)


class File(models.Model):

    """A static file."""

    title = models.CharField(max_length=200,
                             help_text="The title will be used as the default rollover text when this media is embedded in a web page.")

    labels = models.ManyToManyField(
        Label,
        blank=True,
        help_text="Labels are used to help organise your media. They are not visible to users on your website.",
    )

    file = models.FileField(
        upload_to="uploads/files",
        max_length=250,
    )

    def get_absolute_url(self):
        """Generates the absolute URL of the image."""
        return self.file.url

    def __unicode__(self):
        """Returns the title of the media."""
        return self.title

    class Meta:
        ordering = ("title",)

    def is_image(self):
        from .admin import FILE_ICONS, IMAGE_FILE_ICON, UNKNOWN_FILE_ICON

        _, extension = os.path.splitext(self.file.name)
        extension = extension.lower()[1:]
        icon = FILE_ICONS.get(extension, UNKNOWN_FILE_ICON)
        return icon == IMAGE_FILE_ICON


class FileRefField(models.ForeignKey):

    """A foreign key to a File, constrained to only select image files."""

    def __init__(self, **kwargs):
        kwargs["to"] = File
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

    def __unicode__(self):
        """Returns the title of the media."""
        return self.title

    class Meta:
        ordering = ("title",)


class VideoRefField(models.ForeignKey):

    """A foreign key to a File, constrained to only select image files."""

    def __init__(self, **kwargs):
        kwargs["to"] = Video
        kwargs.setdefault("related_name", "+")
        kwargs.setdefault("on_delete", models.PROTECT)
        super(VideoRefField, self).__init__(**kwargs)

    def formfield(self, **kwargs):
        defaults = {
            "widget": ForeignKeyRawIdWidget(self.rel, admin.site),
        }
        return super(VideoRefField, self).formfield(**defaults)
