from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(
        r'^r/(?P<content_type_id>\d+)-(?P<object_id>[^/]+)/$',
        'django.contrib.contenttypes.views.shortcut',
        name='permalink_redirect'
    ),
]
