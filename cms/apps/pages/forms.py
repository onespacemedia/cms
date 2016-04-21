from django import forms

from .models import DEFAULT_LANGUAGE, LANGUAGES_ENGLISH, Page


def generate_page_form(*outer_args, **outer_kwargs):

    class PageForm(forms.ModelForm):

        language = forms.ChoiceField(
            label="Language",
            choices=LANGUAGES_ENGLISH,
            help_text='The current language of the content fields.',
            initial=DEFAULT_LANGUAGE,
        )

        page_type = forms.ChoiceField(
            label="Page type",
            required=False
        )

        title = forms.CharField(
            label="Title",
            widget=forms.TextInput(),
            help_text='The default title'
        )

        slug = forms.CharField(
            label="Slug",
            widget=forms.TextInput(),
            help_text='The part of the title that is used in the URL'
        )

        def __init__(self, *args, **kwargs):
            if 'content_types' in outer_kwargs:
                content_types = outer_kwargs.pop('content_types')
            else:
                content_types = None

            if 'invalid_parents' in outer_kwargs:
                invalid_parents = outer_kwargs.pop('invalid_parents')
            else:
                invalid_parents = None

            super(PageForm, self).__init__(*args, **kwargs)

            if invalid_parents and 'parent' in self.fields:
                self.fields['parent'].choices = [
                    (key, value)
                    for key, value in self.fields['parent'].choices
                    if key
                ]

            self.fields['page_type'].choices = content_types

        class Meta:
            model = Page
            exclude = []

    return PageForm
