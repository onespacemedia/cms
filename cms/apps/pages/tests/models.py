from ..models import ContentBase

class TestMiddlewarePage(ContentBase):
    pass


class TestMiddlewarePageURLs(ContentBase):
    urlconf = 'cms.apps.pages.tests.urls'
