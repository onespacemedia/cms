from django.apps import AppConfig
from watson import search as watson


class PagesAppConfig(AppConfig):
    name = 'cms.apps.pages'

    def ready(self):
        from cms.apps.pages.models import PageSearchAdapter
        Page = self.get_model('Page')
        watson.register(Page, PageSearchAdapter)
