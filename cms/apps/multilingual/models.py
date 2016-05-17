from django.contrib.contenttypes.models import ContentType
from django.db import models
from threadlocals.threadlocals import get_current_request

from cms.apps.pages.models import LANGUAGES_ENGLISH, DEFAULT_LANGUAGE


class MultilingualTranslation(models.Model):
    """ Translation class for content """

    language = models.CharField(
        max_length=2,
        choices=LANGUAGES_ENGLISH,
        default=DEFAULT_LANGUAGE,
        db_index=True
    )

    def __unicode__(self):
        return self.language

    class Meta:
        abstract = True


class MultilingualModel(models.Model):
    """ Container class for translations"""

    translation_cache = {}

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
                translation = self.get_translation(DEFAULT_LANGUAGE)
                return getattr(translation, name)
            except (self.language_model.DoesNotExist, AttributeError):
                return 'Missing translation'

        # Default behaviour
        return self.__getattribute__(name)

    def get_translation(self, language):

        # Check model cache for translation
        if hasattr(self.translation_cache, language):
            return self.translation_cache[language]

        # Missed cache, fetch from DB
        try:
            self.translation_cache[language] = self.translations.select_related().get(language=language)
            return self.translation_cache[language]
        except self.language_model.DoesNotExist:
            return None

    def get_content_type(self):
        return ContentType.objects.get_for_model(self.language_model)

    class Meta:
        abstract = True
