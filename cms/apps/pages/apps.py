from django.apps import AppConfig
from django.db import models
from django.utils.encoding import force_text
from watson import search as watson


class PageSearchAdapter(watson.SearchAdapter):
    def get_content(self, obj):

        content = u" ".join((
            super(PageSearchAdapter, self).get_content(obj),
            self.prepare_content(u" ".join(
                force_text(self._resolve_field(obj.content, field_name))
                for field_name in (
                    field.name for field
                    in obj.content._meta.fields
                    if isinstance(field, (models.CharField, models.TextField))
                )
            ))
        ))

        return content


class PagesAppConfig(AppConfig):
    name = 'cms.apps.pages'

    def ready(self):
        Page = self.get_model("Page")
        watson.register(Page, PageSearchAdapter)
