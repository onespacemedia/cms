'''Models used by the static media management application.'''
import os
import urllib

import requests

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.functional import cached_property
from PIL import Image
from tinypng.api import shrink_file

from .filetypes import get_icon, is_image
from .widgets import ImageThumbnailWidget


class MediaStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if getattr(settings, 'MEDIA_OVERWRITE_WITH_NEW', False):
            self.delete(name)
            return name
        return super().get_available_name(name, max_length)


class Label(models.Model):
    '''
    A label used to organise static media.
    '''

    name = models.CharField(
        max_length=200,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class File(models.Model):
    '''A static file.'''

    title = models.CharField(
        max_length=200,
    )

    labels = models.ManyToManyField(
        Label,
        blank=True,
        help_text='Labels are used to help organise your media. They are not visible to users on your website.',
    )

    file = models.FileField(
        upload_to='uploads/files',
        max_length=250,
        storage=MediaStorage(),
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
        help_text='This text will be used for screen readers. Leave it empty for purely decorative images.',
    )

    date_added = models.DateTimeField(
        default=timezone.now,
    )

    def get_absolute_url(self):
        return self.file.url

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_added', '-pk']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        if self.is_image():
            dimensions = self.get_dimensions()

            if dimensions:
                self.width, self.height = dimensions
                super().save(False, True, using=using, update_fields=update_fields)

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

    @cached_property
    def icon(self):
        return get_icon(self.file.name)

    def is_image(self):
        return is_image(self.file.name)

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
    '''A foreign key to a File.'''

    def __init__(self, **kwargs):
        kwargs['to'] = 'media.File'
        kwargs.setdefault('related_name', '+')
        kwargs.setdefault('on_delete', models.PROTECT)
        super().__init__(**kwargs)

    def formfield(self, **kwargs):
        kwargs.setdefault('widget', ForeignKeyRawIdWidget(self.remote_field, admin.site))
        return super().formfield(**kwargs)


IMAGE_FILTER = {
    'file__iregex': r'\.(png|gif|jpg|jpeg)$'
}


class ImageRefField(FileRefField):
    '''A foreign key to a File, constrained to only select image files.'''

    def __init__(self, **kwargs):
        kwargs['limit_choices_to'] = IMAGE_FILTER
        super().__init__(**kwargs)

    def formfield(self, **kwargs):
        kwargs.setdefault('widget', ImageThumbnailWidget(self.remote_field, admin.site))
        return super().formfield(**kwargs)


VIDEO_FILTER = {
    'file__iregex': r'\.(mp4|m4v)$'
}


def get_oembed_info_url(url):
    '''
    A helper to get the oEmbed information URL for a video.

    This special-cases YouTube videos because bot requests to video pages
    frequently result in the IP being captcha'd out, which breaks the
    auto-discovery mechanism. Fortunately, these IP bans do not seem to apply
    to requests to `/oembed`.
    '''
    youtube_domains = ['youtu.be', 'www.youtube.com', 'youtube.com', 'm.youtube.com']
    vimeo_domains = ['vimeo.com', 'www.vimeo.com']

    if urllib.parse.urlparse(url).netloc in youtube_domains:
        return 'https://www.youtube.com/oembed?format=json&{}'.format(
            urllib.parse.urlencode({'url': url})
        )

    elif urllib.parse.urlparse(url).netloc in vimeo_domains:
        return 'https://vimeo.com/api/oembed.json?{}'.format(
            urllib.parse.urlencode({'url': url})
        )

    # The "not YouTube or Vimeo" case - may get Captcha'd
    # TODO: Send a message to rollbar if this fails
    try:
        req = requests.get(url)
        text = req.text
        soup = BeautifulSoup(text, 'html.parser')
    except:  # pylint:disable=bare-except
        # Either requests failed, or it looked nothing like HTML.
        return None

    # Video providers that support oEmbed will have something that looks like
    # this:
    # <link rel="alternate" type="application/json+oembed" href="...">
    # Where the contents of 'href' tell us where to go to get JSON
    # for an embed code.
    try:
        rel_tag = soup.find(attrs={
            'type': 'application/json+oembed'
        })
        assert rel_tag.get('href')
    except:  # pylint:disable=bare-except
        # This can probably happen if a video is private or deleted.
        return None

    # Now, let's grab the JSON
    return rel_tag.get('href')


def get_video_info(url):
    '''Returns video information for a given URL. Returns a dict in this form:

    {
        'embed_code': '<iframe src=...>',
        'title': 'Title of a video',
    }

    ...or None if no information could be found.
    '''

    if not url or (not url.startswith('http://') and not url.startswith('https://')):
        return

    oembed_url = get_oembed_info_url(url)
    if not oembed_url:
        return

    try:
        req = requests.get(oembed_url)
        json = req.json()
    except:  # pylint:disable=bare-except
        # Bare exception because a lot of possible errors could
        # happen here. Not just requests.exception.RequestException -
        # there's all the ones that could happen in the json library
        # too.
        return None

    # Sanity check.
    if 'html' not in json or not json['html']:
        return None

    video_id = json.get('video_id', None)

    soup = BeautifulSoup(json['html'], 'html.parser')
    src = soup.find('iframe')['src']
    # Remove query string junk
    if src.find('?') > -1:
        src = src[:src.find('?')]

    if not video_id:
        str_index = src.find('embed/') + 6
        video_id = src[str_index:]  # Youtube ids are always 11 characters long

    return {
        'embed_code': json['html'],
        'title': json['title'],
        'service': json['provider_name'].lower(),
        'id': video_id,
        'src': src,
    }


class VideoFileRefField(FileRefField):

    '''A foreign key to a File, constrained to only select video files.'''

    def __init__(self, **kwargs):
        kwargs['limit_choices_to'] = VIDEO_FILTER
        super().__init__(**kwargs)


class Video(models.Model):

    title = models.CharField(
        max_length=200,
    )

    image = ImageRefField(
        blank=True,
        null=True,
    )

    high_resolution_mp4 = VideoFileRefField(
        verbose_name='high resolution MP4',
        blank=True,
        null=True,
    )

    low_resolution_mp4 = VideoFileRefField(
        verbose_name='low resolution MP4',
        blank=True,
        null=True,
    )

    external_video = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Provide a youtube.com or vimeo.com URL.',
    )

    # Secret fields for external videos - populated from the URL when the form is saved.
    external_video_iframe_url = models.TextField(
        null=True,
        blank=True,
    )

    external_video_id = models.CharField(
        max_length=32,
        blank=True,
        null=True,
    )

    external_video_service = models.CharField(
        max_length=32,
        blank=True,
        null=True,
    )
    # End secret fields

    def __str__(self):
        return self.title

    def clean(self):
        if (self.high_resolution_mp4 or self.low_resolution_mp4) and self.external_video:
            raise ValidationError({
                'high_resolution_mp4': 'Please provide either a locally hosted file or an external file, not both.'
            })

        if self.external_video:
            info = get_video_info(self.external_video)
            if info:
                self.external_video_iframe_url = info['src']

                if not self.external_video_iframe_url:
                    raise ValidationError({
                        'external_video': "Couldn't determine how to embed this video. Maybe the video's privacy settings disallow embedding?"
                    })

                self.external_video_id = info['id']
                self.external_video_service = info['service']

        return super().clean()

    def embed_html(self, loop=False, autoplay=False, controls=False, mute=False, youtube_parameters=None):
        '''
        Returns the HTML code for embedding the video.
        Expects youtube_parameters as a dictionary in the form {parameter:value}
        When using, this is a function so call with {{ video.embed_html|safe }}
        '''
        if self.external_video:
            if self.external_video_service == 'youtube':
                return render_to_string('videos/youtube.html', {
                    'src': self.external_video_iframe_url,
                    'autoplay': int(autoplay),
                    'controls': int(controls),
                    'loop': int(loop),
                    'muted': int(mute),
                    'extra_parameters': ('&amp;' + '&amp;'.join('{}={}'.format(parameter, youtube_parameters[parameter]) for parameter in youtube_parameters)) if youtube_parameters else '',
                })
            elif self.external_video_service == 'vimeo':
                return render_to_string('videos/vimeo.html', {
                    'src': self.external_video_iframe_url,
                    'autoplay': int(autoplay),
                    'controls': int(not controls),
                    'loop': int(loop),
                    'muted': int(mute),
                })
            return render_to_string('videos/default.html', {
                'src': self.external_video_iframe_url,
            })
        if self.high_resolution_mp4 or self.low_resolution_mp4:
            return render_to_string('videos/local.html', {
                'preload': 'auto' if autoplay else 'metadata',
                'autoplay': ' autoplay' if autoplay else '',
                'controls': ' controls' if controls else '',
                'loop': ' loop' if loop else '',
                'muted': ' muted' if mute else '',
                'src': self.high_resolution_mp4.file.url if self.high_resolution_mp4 else self.low_resolution_mp4.file.url,
            })

    class Meta:
        ordering = ('title',)


class VideoRefField(models.ForeignKey):
    '''A foreign key to a video, using a raw ID field by default.'''

    def __init__(self, **kwargs):
        kwargs['to'] = 'media.Video'
        kwargs.setdefault('related_name', '+')
        kwargs.setdefault('on_delete', models.PROTECT)
        super().__init__(**kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'widget': ForeignKeyRawIdWidget(self.remote_field, admin.site),
        }
        return super().formfield(**defaults)
