import json

from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe
from django_jinja import library
from django import template
from sorl.thumbnail import get_thumbnail

from ..models import File

register = template.Library()

@library.global_function
def thumbnail(path, geometry, **options):
    return get_thumbnail(path, geometry, **options)


@library.global_function
@register.assignment_tag()
def osm_get_media_list():
    file_list = [{
        'id': file.pk,
        'image': file.file.url,
        'title': file.title,
        'size': filesizeformat(file.file.size),
    } for file in File.objects.all()]

    return mark_safe(json.dumps(file_list))
