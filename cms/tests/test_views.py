from django.test import TestCase
from django.views import generic

from ..views import SearchMetaDetailMixin, TextTemplateView


class TestViews(TestCase):

    def test_texttemplateview_render_to_response(self):
        view = TextTemplateView()
        view.request = {}
        view.template_name = 'templates/base.html'

        rendered = view.render_to_response({})

        self.assertEqual(rendered.template_name, ['templates/base.html'])
        self.assertEqual(rendered.status_code, 200)

    def test_searchmetadetailmixin_get_context_data(self):

        class TestClass(SearchMetaDetailMixin, generic.DetailView):
            class Obj:
                def get_context_data(self):
                    return {'foo': 'bar'}
            object = Obj()

        context = TestClass().get_context_data()
        self.assertIn('foo', context)
        self.assertEqual(context['foo'], 'bar')
