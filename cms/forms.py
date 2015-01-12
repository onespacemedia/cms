"""Form widgets used by the CMS."""
import re
import string

from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm, AdminPasswordChangeForm
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from optimizations import default_stylesheet_cache, default_javascript_cache

from cms import debug

try:
    import json
except:
    from django.utils import simplejson as json


class HtmlWidget(forms.Textarea):

    """A textarea that is converted into a TinyMCE editor."""

    def __init__(self, *args, **kwargs):
        """Initializes the HtmlWidget."""
        self.richtext_settings = getattr(settings, "RICHTEXT_SETTINGS", {}).get(kwargs.pop("richtext_settings", "default"), {})
        super(HtmlWidget, self).__init__(*args, **kwargs)

    @debug.print_exc
    def get_media(self):
        """Returns the media used by the widget."""
        assets = [staticfiles_storage.url("cms/js/tiny_mce/tiny_mce.js")]
        assets.extend(default_javascript_cache.get_urls(("cms/js/jquery.cms.js", "pages/js/jquery.cms.pages.js", "media/js/jquery.cms.media.js",)))
        return forms.Media(js=assets)

    media = property(
        get_media,
        doc = "The media used by the widget.",
    )

    def render(self, name, value, attrs=None):
        """Renders the widget."""

        # Add on the JS initializer.
        attrs = attrs or {}
        attrs['class'] = "tiny-mce"

        # Get the standard widget.
        html = super(HtmlWidget, self).render(name, value, attrs)

        try:
            element_id = attrs["id"]
        except KeyError:
            pass
        else:
            # Customize the config.
            richtext_settings = self.richtext_settings.copy()
            # Cache the asset URL.
            if "content_css" in richtext_settings:
                richtext_settings["content_css"] = default_stylesheet_cache.get_urls((richtext_settings["content_css"],))[0]
            # Add in the initializer.
            settings_js = json.dumps(richtext_settings)
            html += u'<script>django.jQuery("#{element_id}").cms("htmlWidget",{settings_js})</script>'.format(
                element_id = element_id,
                settings_js = settings_js,
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
