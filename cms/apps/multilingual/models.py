from django.core.urlresolvers import reverse
from django.db import models
from exclusivebooleanfield import ExclusiveBooleanField
from threadlocals.threadlocals import get_current_request

from cms.apps.pages.models import DEFAULT_LANGUAGE, LANGUAGES_ENGLISH_DICTIONARY
from cms.apps.pages.models import LANGUAGES_ENGLISH


class MultilingualObject(models.Model):
    admin_name = models.CharField(
        max_length=4096,
        help_text="Name that will be used to identify the object within the admin",
        verbose_name="Name"
    )

    def translation_objects(self):
        return self.translation_object.objects.filter(parent=self)

    def get_translation_add_url(self):
        return '{}?parent={}'.format(
            reverse('admin:{}_{}_add'.format(
                self.translation_object._meta.app_label,
                self.translation_object._meta.model_name
            )),
            self.pk
        )

    def content(self):

        # Get request and current language
        request = get_current_request()
        language = getattr(request, 'language', DEFAULT_LANGUAGE)
        if language is None:
            language = DEFAULT_LANGUAGE

        # Check to see if object has a translation for the current language
        try:

            translation_filter = {
                'language': language
            }

            if not hasattr(request, 'user') or not request.user.is_superuser or request.GET.get('preview', None) is None:
                translation_filter['published'] = True

            translation_queryset = self.translation_objects().filter(
                **translation_filter
            ).order_by('-version')

            return translation_queryset.first()

        except self.translation_object.DoesNotExist:
            return None

    class Meta:
        abstract = True


class MultilingualTranslation(models.Model):
    language = models.CharField(
        max_length=2,
        choices=LANGUAGES_ENGLISH,
        default=DEFAULT_LANGUAGE,
        db_index=True,
        help_text="The language that this translation is for"
    )

    version = models.PositiveIntegerField(
        default=1,
        help_text="Priority is given to the higher number. <br> Using versions you are able to create new language versions without publishing them"
    )

    published = ExclusiveBooleanField(
        on=('parent_id', 'language'),
        default=False,
        help_text="Checking this box will make it the active translation"
    )


    def __unicode__(self):
        return self.parent.admin_name

    def human_language(self):
        return LANGUAGES_ENGLISH_DICTIONARY[self.language]

    def get_change_url(self):
        return reverse('admin:{}_{}_change'.format(
            self._meta.app_label,
            self._meta.model_name
        ), args=[self.pk])

    class Meta:
        abstract = True
        unique_together = ('language', 'version', 'parent')
