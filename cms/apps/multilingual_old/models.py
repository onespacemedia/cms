from django.contrib.contenttypes.models import ContentType
from django.db import models

from cms.apps.pages.models import LANGUAGES_ENGLISH, DEFAULT_LANGUAGE


class MultilingualTranslation(models.Model):
    """ Translation class for content """

    language = models.CharField(
        max_length=2,
        choices=LANGUAGES_ENGLISH,
        default=DEFAULT_LANGUAGE,
        db_index=True
    )

    version = models.PositiveIntegerField(
        default=1,
        help_text="Version number of the language. A higher version has a higher priority."
    )

    online = models.BooleanField(
        default=False,
        help_text="Unchecking this box allows you to create / edit it without putting it live."
    )

    def __unicode__(self):
        return self.language

    class Meta:
        abstract = True
        unique_together = ("parent", "language", "version",)


class MultilingualModel(models.Model):
    """ Container class for translations"""

    default_language = models.CharField(
        max_length=2,
        choices=LANGUAGES_ENGLISH,
        default=DEFAULT_LANGUAGE,
        db_index=True
    )

    def __init__(self, *args, **kwargs):
        super(MultilingualModel, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return 'Multilingual Object'

    def __getattr__(self, name):

        # Check to see if the attr is in the list of fields that are potentially translatable
        language_fields = self.language_model._meta.get_all_field_names()
        if name in language_fields:

            # Try to get a translation for the default language
            try:
                translation = self.get_translation(self.default_language)
                return getattr(translation, name)
            except (self.language_model.DoesNotExist, AttributeError):
                return 'N/A'

        # Default behaviour
        return self.__getattribute__(name)

    def get_translation(self, language):

        # Missed cache, fetch from DB
        try:
            return self.translations.select_related().order_by('-version').filter(language=language)[0]
        except IndexError:
            return None

    def get_content_type(self):
        return ContentType.objects.get_for_model(self.language_model)

    class Meta:
        abstract = True
