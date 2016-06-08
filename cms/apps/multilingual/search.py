from django.db import models
from django.utils.encoding import force_text
from watson import search as watson


class MultilingualSearchAdapter(watson.SearchAdapter):

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
