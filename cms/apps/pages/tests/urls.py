from django.conf.urls import url
from django.http import Http404


def view(request, *args, **kwargs):
    if request.path == '/raise404/':
        raise Http404
    return None

urlpatterns = [
    url("^$", view, name="index"),
    url("^(?P<slug>[^/]+)/$", view, name="detail"),
]
