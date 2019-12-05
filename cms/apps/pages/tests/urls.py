from django.conf.urls import url
from django.http import Http404, HttpResponse


def view(request, *args, **kwargs):
    if request.path == '/raise404/':
        raise Http404
    return HttpResponse('Hello!')


urlpatterns = [
    url("^$", view, name="index"),
    url("^(?P<slug>[^/]+)/$", view, name="detail"),
]
