from cms.apps.pages.models import Page
from haystack import indexes


class PageIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Page

    def index_queryset(self, using=None):
        return self.get_model().objects.filter()
