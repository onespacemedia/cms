import json

from django import forms
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.safestring import mark_safe


class HtmlWidget(forms.Textarea):
    '''A textarea that is converted into a TinyMCE rich text editor.'''

    def get_media(self):
        '''Returns the media used by the widget.'''
        js = [
            staticfiles_storage.url('cms/js/tinymce/tinymce.min.js'),
            staticfiles_storage.url('cms/js/jquery.cms.wysiwyg.js'),
        ]

        css = {}

        return forms.Media(js=js, css=css)

    media = property(
        get_media,
        doc='The media used by the widget.',
    )

    def render(self, name, value, attrs=None, renderer=None):
        '''Renders the widget.'''

        # Add on the JS initializer.
        attrs = attrs or {}
        attrs['class'] = 'wysiwyg'
        attrs['required'] = False
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
        attrs['data-wysiwyg-settings'] = json.dumps(wysiwyg_settings)

        # Get the standard widget.
        html = super().render(name, value, attrs)

        return mark_safe(html)
