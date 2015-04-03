from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm, AdminPasswordChangeForm
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from cms import debug

import json
import re
import string


class HtmlWidget(forms.Textarea):

    """A textarea that is converted into a Redactor editor."""

    def __init__(self, *args, **kwargs):
        """Initializes the HtmlWidget."""
        super(HtmlWidget, self).__init__(*args, **kwargs)

    @debug.print_exc
    def get_media(self):
        """Returns the media used by the widget."""
        js = [
            staticfiles_storage.url("cms/js/jquery.cms.js"),
            staticfiles_storage.url("cms/js/jquery.cookie.js"),
            staticfiles_storage.url("pages/js/jquery.cms.pages.js"),
            staticfiles_storage.url("cms/js/redactor/redactor.js"),
        ] + [
            staticfiles_storage.url('cms/js/redactor/plugins/{plugin}/{plugin}.js'.format(plugin=plugin))
            for plugin in getattr(settings, 'REDACTOR_OPTIONS', {}).get('plugins', [])
        ]

        css = {
            "all": [
                "cms/js/redactor/redactor.css"
            ]
        }
        return forms.Media(js=js, css=css)

    media = property(
        get_media,
        doc="The media used by the widget.",
    )

    def render(self, name, value, attrs=None):
        """Renders the widget."""

        # Add on the JS initializer.
        attrs = attrs or {}
        attrs['class'] = "redactor"

        # Get the standard widget.
        html = super(HtmlWidget, self).render(name, value, attrs)

        try:
            element_id = attrs["id"]
        except KeyError:
            pass
        else:
            # Add in the initializer.
            html += '<script>django.jQuery("#{element_id}").redactor({settings_js});</script>'.format(
                element_id=element_id,
                settings_js=json.dumps(getattr(settings, 'REDACTOR_OPTIONS', {})),
            )
        # All done!
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
