from django.urls import reverse
from django_jinja import library
from django import template
from sorl.thumbnail import get_thumbnail

register = template.Library()

@library.global_function
def thumbnail(path, geometry, **options):
    return get_thumbnail(path, geometry, **options)


@library.global_function
@register.assignment_tag()
def osm_image_upload_path():
    return reverse('admin_image_upload')
