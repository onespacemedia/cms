import json

from django import VERSION
from django.conf import settings
from django.test import TestCase
from django.utils.html import conditional_escape

from ..forms import HtmlWidget


class MockSuperUser:

    pk = 1

    def check_password(self, password):
        return True

    def has_perm(self, perm):
        return True


class TestForms(TestCase):

    def test_htmlwidget_init(self):
        widget = HtmlWidget()
        self.assertIsInstance(widget, HtmlWidget)

    def test_htmlwidget_get_media(self):
        widget = HtmlWidget()

        media = widget.get_media()

        if (VERSION[0], VERSION[1]) == (1, 11):
            self.assertDictEqual(media.__dict__, {
                '_css': {},
                '_js': [
                    '/static/cms/js/tinymce/tinymce.min.js',
                    '/static/cms/js/jquery.cms.wysiwyg.js',
                ],
            })
        else:
            self.assertDictEqual(media.__dict__, {
                '_css_lists': [{}],
                '_js_lists': [[
                    '/static/cms/js/tinymce/tinymce.min.js',
                    '/static/cms/js/jquery.cms.wysiwyg.js',
                ]],
            })

    def test_htmlwidget_render(self):
        # Sorry for the long strings in this one..
        widget = HtmlWidget()
        rendered = widget.render('foo', 'bar')

        wysiwyg_settings = {
            'branding': False,
            'codemirror': {
                'indentOnInit': True,
                'fullscreen': False,
                'path': 'codemirror',
                'config': {
                    'lineNumbers': True,
                    'lineWrapping': True
                },
                'width': 800,
                'height': 600,
                'saveCursorPosition': True
            }
        }
        wysiwyg_settings.update(getattr(settings, 'WYSIWYG_OPTIONS', {}))

        self.assertInHTML(
            rendered,
            '<textarea name="foo" rows="10" cols="40" data-wysiwyg-settings="{}" class="wysiwyg">\nbar</textarea>'.format(
                conditional_escape(json.dumps(wysiwyg_settings))
            ),
        )

        rendered = widget.render('foo', 'bar', attrs={'id': 'foo'})

        self.assertInHTML(
            '<textarea name="foo" class="wysiwyg" rows="10" cols="40" data-wysiwyg-settings="{}" id="foo">\nbar</textarea>'.format(
                conditional_escape(json.dumps(wysiwyg_settings))
            ),
            rendered,
        )
