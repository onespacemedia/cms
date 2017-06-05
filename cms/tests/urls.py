from django.conf.urls import url, include
from django.contrib import admin

from django.contrib.contenttypes.views import shortcut


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(
        r'^r/(?P<content_type_id>\d+)-(?P<object_id>[^/]+)/$',
        shortcut,
        name='permalink_redirect'
    ),
]
