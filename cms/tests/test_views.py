from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.views import generic
from six import text_type

from ..views import SearchMetaDetailMixin, TextTemplateView, CacheMixin


class CacheTestView(CacheMixin, generic.View):
    def dispatch(self, request, *args, **kwargs):
        return HttpResponse('foo')


class TestViews(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

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

    def test_cachemixin(self):
        test_view = CacheTestView()

        self.assertEqual(test_view.get_cache_timeout(), test_view.cache_timeout)

        for do_caching in [True, False]:
            with self.settings(CMS_CACHE_PAGES=do_caching):
                request = self.factory.get('/')
                response = test_view.dispatch(request)
                self.assertEqual(response.content, text_type('foo'))
