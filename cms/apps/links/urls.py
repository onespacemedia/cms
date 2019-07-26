'''URLs used by the links application.'''

from django.conf.urls import url

from cms.apps.links.views import index

urlpatterns = [
    url(r'^$', index, name='index'),
]
