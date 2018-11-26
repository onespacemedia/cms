from django_jinja import library
from sorl.thumbnail import get_thumbnail


@library.global_function
def thumbnail(path, geometry, **options):
    return get_thumbnail(path, geometry, **options)
