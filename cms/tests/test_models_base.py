from django.test import TestCase, RequestFactory

from ..models.base import (PublishedBaseSearchAdapter as CMSPublishedBaseSearchAdapter,
                           SearchMetaBaseSearchAdapter as CMSSearchMetaBaseSearchAdapter,
                           PageBase, PublishedBase, SearchMetaBase)


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
        self.assertDictEqual(obj.get_context_data(), {
            'meta_description': '',
            'robots_follow': True,
            'robots_index': True,
            'title': 'TestSearchMetaBaseModel object',
            'robots_archive': True,
            'header': 'TestSearchMetaBaseModel object',
            'og_title': '',
            'og_description': '',
            'og_image': None,
            'twitter_card': None,
            'twitter_title': '',
            'twitter_description': '',
            'twitter_image': None
        })

    def test_searchmetabase_render(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.pages = []

        obj = TestSearchMetaBaseModel.objects.create()
        response = obj.render(request, '../templates/pagination/pagination.html')

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
