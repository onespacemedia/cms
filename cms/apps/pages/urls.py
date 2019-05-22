'''URLs used by ContentBase derivatives.'''

from django.conf.urls import url
from django.views.decorators.csrf import csrf_protect

from cms.apps.pages import views

urlpatterns = [
    url(r'^$', csrf_protect(views.ContentIndexView.as_view()), name='index')
]
