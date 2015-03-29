from django.test import TestCase

from ..views import TextTemplateView


class TestViews(TestCase):

    def test_texttemplateview_render_to_response(self):
        view = TextTemplateView()
        view.request = {}
        view.template_name = 'templates/base.html'

        rendered = view.render_to_response({})

        self.assertEqual(rendered.template_name, ['templates/base.html'])
        self.assertEqual(rendered.status_code, 200)
