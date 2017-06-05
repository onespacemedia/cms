from django.template.loader import render_to_string
from django_jinja import library
from sorl.thumbnail import get_thumbnail


@library.global_function
def thumbnail(path, geometry, **options):
    return get_thumbnail(path, geometry, **options)


@library.global_function
def render_video(video, prefer_high_res=True):
    '''Returns an embed code for the video.'''
    context = {
        'video': video,
    }
    return render_to_string('media/video.html')
