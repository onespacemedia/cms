from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase
from watson.search import update_index

from ...pages.models import Page
from ..models import Link
from ..views import index


class TestLinks(TestCase):

    def test_index_redirect(self):
        with update_index():
            page = Page.objects.create(
                title='Homepage',
                content_type=ContentType.objects.get_for_model(Link),
            )

            Link.objects.create(
                page=page,
                link_url='http://www.example.com/',
                permanent=False,
            )

        factory = RequestFactory()
        request = factory.get('/')

        class Object:
            pass

        setattr(request, 'pages', Object)
        request.pages.current = page
        view = index(request)

        self.assertEquals(view.status_code, 302)
        self.assertEquals(view['Location'], 'http://www.example.com/')

        with update_index():
            page = Page.objects.create(
                title='Permanent redirect',
                slug='permanent-redirect',
                content_type=ContentType.objects.get_for_model(Link),
                parent=page,
            )

            link = Link.objects.create(
                page=page,
                link_url='http://www.example.com/',
                permanent=True,
            )

        request = factory.get('/permanent-redirect/')

        setattr(request, 'pages', Object)
        request.pages.current = page
        view = index(request)
