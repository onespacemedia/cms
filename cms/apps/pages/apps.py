from django.apps import AppConfig
from django.db import models
from django.utils.encoding import force_text
from watson import search as watson
from watson.search import SearchAdapter


class PageSearchAdapter(SearchAdapter):
    def get_url(self, obj):
        if obj.content and hasattr(obj.content, 'get_absolute_url'):
            return obj.content.get_absolute_url()

        return ''

    def get_content(self, obj):
        if obj.content:
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

        return ""

    def get_live_queryset(self):
        """Selects only live models."""
        qs = self.model.objects.all()
        return qs.exclude(
            pk__in=[
                page.id for page in qs
                if page.content and page.content.hide_from_search
            ]
        )


class PagesAppConfig(AppConfig):
    name = 'cms.apps.pages'

    def ready(self):
        Page = self.get_model("Page")
        watson.register(Page, PageSearchAdapter)
