"""HTML processing routines."""
from __future__ import unicode_literals

import six
from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from sorl.thumbnail import get_thumbnail

from cms import permalinks


def process(text):
    """
    Expands permalinks in <a/> and <img/> tags.

    Images will also be automatically thumbnailed to fit their specified width
    and height.
    """
    resolved_permalinks = {}

    def get_obj(element, attribute):
        value = element.get(attribute)
        if value:
            if value not in resolved_permalinks:
                try:
                    resolved_permalinks[value] = permalinks.resolve(value)
                except (permalinks.PermalinkError, ObjectDoesNotExist):
                    resolved_permalinks[value] = None
            obj = resolved_permalinks[value]
            return obj
        return None

    soup = BeautifulSoup(text, 'html.parser')
    text_anchors = soup.find_all('a')
    text_images = soup.find_all('img')
    for link in text_anchors:
        obj = get_obj(link, 'href')
        if obj:
            link['href'] = obj.get_absolute_url()
            link['title'] = getattr(obj, 'title', str(obj))

    for image in text_images:
        obj = get_obj(image, 'src')
        if obj:
            image['src'] = obj.get_absolute_url()
            image['title'] = getattr(obj, 'title', str(obj))
            if hasattr(obj, 'attribution') or hasattr(obj, 'copyright'):
                title = ''

                if hasattr(obj, 'copyright') and obj.copyright:
                    title += six.text_type('\xa9 {}. '.format(obj.copyright))

                if hasattr(obj, 'attribution') and obj.attribution:
                    title += obj.attribution

                if title:
                    image['title'] = title

            try:
                width = int(image.get('width'))
                height = int(image.get('height'))
            except (ValueError, KeyError, TypeError):
                pass
            else:
                # Automagically detect a FileField.
                fieldname = None
                for field in obj._meta.fields:
                    if isinstance(field, models.FileField):
                        fieldname = field.name
                # Generate the thumbnail.
                if fieldname:
                    try:
                        thumbnail = get_thumbnail(getattr(obj, fieldname), '{}x{}'.format(width, height), quality=99, format="PNG")
                    except IOError:
                        pass
                    else:
                        image['src'] = thumbnail.url
                        image['width'] = thumbnail.width
                        image['height'] = thumbnail.height

    return six.text_type(soup.decode(formatter='html5'))

