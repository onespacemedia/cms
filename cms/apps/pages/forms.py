from django import forms

from .models import Page


class PageVersionListForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['parent', 'slug']
