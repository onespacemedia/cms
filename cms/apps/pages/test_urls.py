import re

from django.conf.urls import url
from django.core import urlresolvers
from django.views.decorators.csrf import csrf_protect

from . import views
from .models import Page


def generate_urlpatterns():
    urlpatterns = []
    pages = Page.objects.all()

    for page in pages:
        page_url = page.get_absolute_url()[1:]

        if not page.parent:
            page_url = '/'

        if page.content.urlconf != 'cms.apps.pages.urls':
            callback, callback_args, callback_kwargs = urlresolvers.resolve('/', page.content.urlconf)

            urlpatterns.append(
                url(
                    r'^{}$'.format(re.escape(page_url)),
                    callback,
                )
            )
        else:
            urlpatterns.append(
                url(
                    r'^{}$'.format(re.escape(page_url)),
                    csrf_protect(views.ContentIndexView.as_view()),
                    name="index"
                )
            )

    return urlpatterns


urlpatterns = generate_urlpatterns()
