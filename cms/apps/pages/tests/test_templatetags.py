import base64
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory, Client
from django.utils import six
from django.utils.timezone import now
from cms.apps.media.models import File

from ..middleware import RequestPageManager
from ..models import ContentBase, Page, Country
from ..templatetags.pages import get_navigation, page_url, breadcrumbs, country_code, og_image, absolute_domain_url, \
    twitter_image, twitter_card, twitter_title, twitter_description
from .... import externals

import random


class MockUser(object):
    def __init__(self, authenticated=True):
        self.authenticated = authenticated

    def is_authenticated(self):
        return self.authenticated


class TestTemplatetagPage(ContentBase):
    urlconf = 'cms.apps.pages.tests.urls'


class TestTemplatetags(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

        # A valid GIF.
        self.name_1 = '{}-{}.gif'.format(
            now().strftime('%Y-%m-%d_%H-%M-%S'),
            random.randint(0, six.MAXSIZE)
        )

        base64_string = b'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
        self.obj_1 = File.objects.create(
            title="Foo",
            file=SimpleUploadedFile(self.name_1, base64.b64decode(base64_string), content_type="image/gif")
        )

        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(TestTemplatetagPage)

            self.homepage = Page.objects.create(
                title="Homepage",
                slug='homepage',
                content_type=content_type,
            )

            TestTemplatetagPage.objects.create(
                page=self.homepage,
            )

            self.section = Page.objects.create(
                parent=self.homepage,
                title="Section",
                slug='section',
                content_type=content_type,
                hide_from_anonymous=True
            )

            TestTemplatetagPage.objects.create(
                page=self.section,
            )

            self.subsection = Page.objects.create(
                parent=self.section,
                title="Subsection",
                content_type=content_type,
            )

            TestTemplatetagPage.objects.create(
                page=self.subsection,
            )

            self.subsubsection = Page.objects.create(
                parent=self.subsection,
                title="Subsubsection",
                content_type=content_type,
            )

            TestTemplatetagPage.objects.create(
                page=self.subsubsection,
            )

    def tearDown(self):
        self.obj_1.file.delete(False)
        self.obj_1.delete()

    def test_get_navigation(self):
        request = self.factory.get('/')
        request.user = MockUser(authenticated=True)
        request.pages = RequestPageManager(request)

        navigation = get_navigation({'request': request}, request.pages.current.navigation)

        self.assertListEqual(navigation, [
            {
                'url': '/section/',
                'page': self.section,
                'here': False,
                'title': 'Section'
            }
        ])

        # Section page isn't visible to non logged in users
        request.user = MockUser(authenticated=False)

        navigation = get_navigation({'request': request}, request.pages.current.navigation)

        self.assertListEqual(navigation, [])

    def test_page_url(self):
        self.assertEqual(page_url(self.homepage), '/')
        self.assertEqual(page_url(self.homepage.pk), '/')
        self.assertEqual(page_url(-1), '#')
        self.assertEqual(page_url(None), '#')
        self.assertEqual(
            page_url(self.homepage.pk, 'detail', slug='homepage'),
            '/homepage/'
        )

    def test_breadcrumbs(self):
        class Object(object):
            current = None

        self.request.pages = Object()

        output = breadcrumbs({'request': self.request}, extended=True)
        self.assertDictEqual(output, {
            'breadcrumbs': []
        })

    def test_country_code(self):
        class Context(object):
            pass

        context = Context()
        context.request = self.request
        self.assertEqual(country_code(context), '')

        country = Country.objects.create(
            code='GB',
        )

        context = Context()
        context.request = self.request
        context.request.country = country
        self.assertEqual(country_code(context), '/gb')

    def test_open_graph_tags(self):
        request = self.factory.get('/')
        request.user = MockUser(authenticated=True)
        request.pages = RequestPageManager(request)

        context = {}
        context['request'] = request

        self.assertEqual(twitter_card(context), '')
        self.assertEqual(twitter_title(context), 'Homepage')
        self.assertEqual(twitter_description(context), '')

        context['twitter_card'] = 1
        context['twitter_title'] = 'Title'
        context['twitter_description'] = 'Description'

        self.assertEqual(twitter_card(context), 'photo')
        self.assertEqual(twitter_title(context), 'Title')
        self.assertEqual(twitter_description(context), 'Description')

    def test_image_obj(self):
        request = self.factory.get('/')
        request.user = MockUser(authenticated=True)
        request.pages = RequestPageManager(request)

        context = {}
        context['request'] = request
        context['og_image'] = context['twitter_image'] = self.obj_1

        self.assertEqual(og_image(context), '{}{}'.format(
            absolute_domain_url(context),
            self.obj_1.get_absolute_url()
        ))

        self.assertEqual(twitter_image(context), '{}{}'.format(
            absolute_domain_url(context),
            self.obj_1.get_absolute_url()
        ))

        context['twitter_image'] = None

        self.assertEqual(twitter_image(context), '{}{}'.format(
            absolute_domain_url(context),
            self.obj_1.get_absolute_url()
        ))
