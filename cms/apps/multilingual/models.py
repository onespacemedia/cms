from django.db import models
from threadlocals.threadlocals import get_current_request

LANGUAGES = [
    ('en', ['English', 'English']),
    ('de', ['German', 'Deutsch']),
]

LANGUAGES_ENGLISH = [
    (x[0], x[1][0])
    for x in LANGUAGES
]

DEFAULT_LANGUAGE = 'en'


class MultilingualTranslation(models.Model):
    """ Translation class for content """

    language = models.CharField(
        max_length=2,
        choices=LANGUAGES_ENGLISH,
        default=DEFAULT_LANGUAGE,
        db_index=True
    )

    class Meta:
        abstract = True


class MultilingualModel(models.Model):
    """ Container class for translations"""

    def __init__(self):
        request = get_current_request()
        self.language = getattr(request, 'language', 'en')

    # Override default attribution getter to return
    def __getattr__(self, item):

        # Return item if it exists in this model
        if item in self.__dict__:
            return self.__dict__[item]

        # Item not found
        return None

    class Meta:
        abstract = True
