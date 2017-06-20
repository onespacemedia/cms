import json
import re
# https://www.logilab.org/ticket/2481
import string  # pylint: disable=deprecated-module

from django import forms
from django.conf import settings
from django.contrib.auth.forms import (AdminPasswordChangeForm,
                                       PasswordChangeForm)
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from cms import debug


class HtmlWidget(forms.Textarea):
    """A textarea that is converted into a Redactor editor."""

    @debug.print_exc
    def get_media(self):
        """Returns the media used by the widget."""
        js = [
            staticfiles_storage.url("cms/js/tinymce/tinymce.min.js"),
            staticfiles_storage.url("cms/js/jquery.cms.wysiwyg.js"),
        ]

        css = {}

        return forms.Media(js=js, css=css)

    media = property(
        get_media,
        doc="The media used by the widget.",
    )

    def render(self, name, value, attrs=None, renderer=None):
        """Renders the widget."""

        # Add on the JS initializer.
        attrs = attrs or {}
        attrs['class'] = "wysiwyg"
        attrs['required'] = False
        attrs['data-wysiwyg-settings'] = json.dumps(
            getattr(settings, 'WYSIWYG_OPTIONS', {})
        )

        # Get the standard widget.
        html = super(HtmlWidget, self).render(name, value, attrs)

        return mark_safe(html)

# Checks a string against some rules
def password_validation(password):
    errors = []

    if len(password) < 8:
        errors.append('Your password needs to be at least 8 characters long.')

    if password.lower() == password:
        errors.append('Your password needs include at least 1 uppercase character.')

    if password.upper() == password:
        errors.append('Your password needs include at least 1 lowercase character.')

    if not re.findall(r"[\d]", password):
        errors.append('Your password needs include at least 1 number.')

    if not re.findall(r"[{}]".format(re.escape(string.punctuation)), password):
        errors.append('Your password needs include at least 1 special character.')

    return errors


class CMSPasswordChangeForm(PasswordChangeForm):

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if password_validation(password):
            raise ValidationError([
                ValidationError(error) for error in password_validation(password)
            ])
        return password


class CMSAdminPasswordChangeForm(AdminPasswordChangeForm):

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password_validation(password):
            raise ValidationError([
                ValidationError(error) for error in password_validation(password)
            ])
        return password
