from django.test import RequestFactory, TestCase

from ..models.base import \
    PublishedBaseSearchAdapter as CMSPublishedBaseSearchAdapter
from ..models.base import \
    SearchMetaBaseSearchAdapter as CMSSearchMetaBaseSearchAdapter
from ..models.base import PageBase, PublishedBase, SearchMetaBase


# Test models.
class TestPublishedBaseModel(PublishedBase):
    pass


class TestSearchMetaBaseModel(SearchMetaBase):
    pass


class PageBaseModel(PageBase):
    pass


# Test search adapters.
class PublishedBaseSearchAdapter(CMSPublishedBaseSearchAdapter):
    pass


class SearchMetaBaseSearchAdapter(CMSSearchMetaBaseSearchAdapter):
    pass


class ModelsBaseTest(TestCase):

    def test_publishedbasesearchadapter_get_live_queryset(self):
        search_adapter = PublishedBaseSearchAdapter(TestPublishedBaseModel)
        self.assertEqual(search_adapter.get_live_queryset().count(), 0)

        TestPublishedBaseModel.objects.create()
        self.assertEqual(search_adapter.get_live_queryset().count(), 1)

    def test_searchmetabase_get_context_data(self):
        obj = TestSearchMetaBaseModel.objects.create()
        expected_context = {
            'meta_description': '',
            'robots_follow': True,
            'robots_index': True,
            # This differs from 1.11 to 2.x - 2.x puts the PK in the default
            # __str__.
            'title': ['TestSearchMetaBaseModel object', f'TestSearchMetaBaseModel ({obj.pk})'],
            'robots_archive': True,
            'header': ['TestSearchMetaBaseModel object', f'TestSearchMetaBaseModel ({obj.pk})'],
            'og_title': '',
            'og_description': '',
            'og_image': None,
            'twitter_card': None,
            'twitter_title': '',
            'twitter_description': '',
            'twitter_image': None
        }

        for key, value in obj.get_context_data().items():
            if isinstance(expected_context[key], list):
                self.assertIn(value, expected_context[key])
            else:
                self.assertEqual(value, expected_context[key])

    def test_searchmetabase_render(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.pages = []

        class Context(dict):
            pass

        context = Context()
        context['page_obj'] = Context()
        context['page_obj'].has_other_pages = lambda: False

        obj = TestSearchMetaBaseModel.objects.create()
        response = obj.render(request, 'pagination/pagination.html', context)

        self.assertEqual(response.status_code, 200)

    def test_searchmetabasesearchadapter_get_live_queryset(self):
        search_adapter = SearchMetaBaseSearchAdapter(TestSearchMetaBaseModel)
        self.assertEqual(search_adapter.get_live_queryset().count(), 0)

        TestSearchMetaBaseModel.objects.create()
        self.assertEqual(search_adapter.get_live_queryset().count(), 1)

    def test_pagebasemodel_get_context_data(self):
        obj = PageBaseModel.objects.create()
        self.assertDictEqual(obj.get_context_data(), {
            'meta_description': '',
            'robots_follow': True,
            'robots_index': True,
            'title': '',
            'robots_archive': True,
            'header': '',
            'og_title': '',
            'og_description': '',
            'og_image': None,
            'twitter_card': None,
            'twitter_title': '',
            'twitter_description': '',
            'twitter_image': None
        })
