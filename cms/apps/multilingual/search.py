from django.db import models
from django.utils.encoding import force_text
from threadlocals.threadlocals import get_current_request
from watson import search as watson

from cms.apps.pages.models import DEFAULT_LANGUAGE


class MultilingualSearchAdapter(watson.SearchAdapter):

    def get_url(self, obj):
        if hasattr(obj, 'content') and obj.content() is not None:
            return obj.content().get_absolute_url()

        return ''

    def get_content(self, obj):

        if obj.content():
            content = u" ".join((
                super(MultilingualSearchAdapter, self).get_content(obj),
                self.prepare_content(u" ".join(
                    force_text(self._resolve_field(obj.content(), field_name))
                    for field_name in (
                        field.name for field
                        in obj.content()._meta.fields
                        if isinstance(field, (models.CharField, models.TextField))
                    )
                ))
            ))
        else:
            content = u" ".join((
                super(MultilingualSearchAdapter, self).get_content(obj),
            ))

        return content

    def get_live_queryset(self):

        request = get_current_request()
        language = DEFAULT_LANGUAGE

        if hasattr(request, 'language'):
            request.language

        filter = {}
        filter['page__isnull'] = False
        filter['{}__published'.format(self.model.translation_object.__name__.lower())] = True
        filter['{}__language'.format(self.model.translation_object.__name__.lower())] = language

        queryset = self.model.objects.filter(
            **filter
        ).distinct()

        return queryset

