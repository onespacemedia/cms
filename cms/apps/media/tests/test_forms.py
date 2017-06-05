import requests
import requests_mock

from django import forms
from django.test import LiveServerTestCase, RequestFactory, TestCase

from ..forms import IframeFindingParser, OEmbedFindingParser, VideoAdminForm


class TestOEmbedFindingParser(TestCase):
    '''Tests the oEmbed finding parser.'''
    def setUp(self):
        self.oembed_parser_good = OEmbedFindingParser()
        self.oembed_parser_good.feed('<link type="application/json+oembed" href="http://www.onespacemedia.com">')

        self.oembed_parser_ignored_1 = OEmbedFindingParser()
        self.oembed_parser_ignored_1.feed('<p>Not a link tag</p>')

        self.oembed_parser_ignored_2 = OEmbedFindingParser()
        self.oembed_parser_ignored_2.feed('<link rel="no-href-attribute">')

        self.assertTrue(hasattr(self.oembed_parser_good, 'oembed_url'))

    def test_handle_starttag(self):
        self.assertEquals(self.oembed_parser_good.oembed_url, 'http://www.onespacemedia.com')
        self.assertEquals(self.oembed_parser_ignored_1.oembed_url, None)
        self.assertEquals(self.oembed_parser_ignored_2.oembed_url, None)


class TestIframeFindingParser(TestCase):
    '''Tests the <iframe> `src`-attribute finding parser.'''
    def setUp(self):
        self.iframe_parser_good = IframeFindingParser()
        self.iframe_parser_good.feed('<iframe src="http://www.onespacemedia.com"></iframe>')

        self.iframe_parser_ignored_1 = IframeFindingParser()
        self.iframe_parser_ignored_1.feed('<iframe>No src attribute</iframe>')

        self.iframe_parser_ignored_2 = IframeFindingParser()
        self.iframe_parser_ignored_2.feed('<p>Some other element.</p>')

        self.assertTrue(hasattr(self.iframe_parser_good, 'iframe_url'))

    def test_handle_starttag(self):
        self.assertEquals(self.iframe_parser_good.iframe_url, 'http://www.onespacemedia.com')
        self.assertEquals(self.iframe_parser_ignored_1.iframe_url, None)
        self.assertEquals(self.iframe_parser_ignored_2.iframe_url, None)


class TestVideoAdminForm(LiveServerTestCase):
    def setUp(self):
        self.good_json_data = {
            'html': '<iframe src="http://www.example.com/MOCKED_IFRAME_URL/"></iframe>'
        }

        self.good_html = '<html><link rel="alternate" type="application/json+oembed" href="http://www.example.com/MOCKED_OEMBED_URL/"></html>'

    def test_clean(self):
        data = {
            'title': 'Test video',
        }

        # form = VideoAdminForm(data)
        # self.assertTrue(form.is_valid())

        # Tests for various broken URLs.
        with requests_mock.Mocker() as mocker:
            # A good URL.
            mocker.register_uri('GET', 'https://www.example.com/MOCK_404/', text='404', status_code=404)
            mocker.register_uri('GET', 'https://www.example.com/MOCK_NO_OEMBED/', text='<html></html>')

            # All these should fail.
            for url in [
                'https://www.example.com/MOCK_404/',
                'https://www.example.com/MOCK_NO_OEMBED/'
            ]:
                data['external_url'] = url
                form = VideoAdminForm(data)
                self.assertFalse(form.is_valid())

    def test_iframe_url_from_json(self):
        # Test some random bad JSON data
        bad_json = {}

        # This one just doesn't have a good <iframe> tag.
        bad_json_2 = {
            'html': '<object></object>'
        }

        form = VideoAdminForm()

        with self.assertRaises(forms.ValidationError):
            form._iframe_url_from_json(bad_json)

        with self.assertRaises(forms.ValidationError):
            form._iframe_url_from_json(bad_json_2)

        self.assertEquals(form._iframe_url_from_json(self.good_json_data), 'http://www.example.com/MOCKED_IFRAME_URL/')

    def test_oembed_url_from_html(self):
        form = VideoAdminForm()

        # Deliberately terrible HTML that chokes python's HTML parser.
        with self.assertRaises(forms.ValidationError):
            form._oembed_url_from_html('<![..]>')

        # Random HTML.
        with self.assertRaises(forms.ValidationError):
            form._oembed_url_from_html('<html><p></p></html>')

        self.assertEquals(form._oembed_url_from_html(self.good_html), 'http://www.example.com/MOCKED_OEMBED_URL/')
