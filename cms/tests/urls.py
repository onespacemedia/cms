from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.contenttypes.views import shortcut

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(
        r'^r/(?P<content_type_id>\d+)-(?P<object_id>[^/]+)/$',
        shortcut,
        name='permalink_redirect'
    ),
]
