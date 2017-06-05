import requests
from django import forms
from six.moves import html_parser

from .models import Video


# Interestingly, py2's HTMLParser does not inherit from `object`...
class OEmbedFindingParser(html_parser.HTMLParser, object):
    """A small parser that does nothing but get the URL referred to in the
    first <link> attribute with type='application/json+oembed'."""
    def __init__(self, *args, **kwargs):
        super(OEmbedFindingParser, self).__init__(*args, **kwargs)
        self.oembed_url = None

    def handle_starttag(self, tag, attrs):
        # Video providers that support oEmbed will have something that looks
        # like this:
        #   <link rel="alternate" type="application/json+oembed" href="...">
        # Where the contents of 'href' tell us where to go to get JSON
        # for an embed code.
        if not tag == "link":
            return
        attrs_d = dict(attrs)
        if "href" not in attrs_d or "type" not in attrs_d:
            return
        if attrs_d["type"] == "application/json+oembed":
            self.oembed_url = attrs_d["href"]


class IframeFindingParser(html_parser.HTMLParser, object):
    def __init__(self, *args, **kwargs):
        super(IframeFindingParser, self).__init__(*args, **kwargs)
        self.iframe_url = None

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        if tag == 'iframe' and 'src' in attrs_d:
            self.iframe_url = attrs_d['src']


class VideoAdminForm(forms.ModelForm):
    """Custom admin form for Video model."""

    class Meta:
        model = Video
        exclude = ["iframe_url"]

    def clean(self):
        cleaned_data = super(VideoAdminForm, self).clean()

        url = cleaned_data.get("external_url")

        if url:
            # Get the contents of the URL field.
            try:
                req = requests.get(url)
                text = req.text
            except requests.exception.RequestException:
                raise forms.ValidationError(
                    "Unable to get video URL. Please try saving again."
                )

            oembed_url = self._oembed_url_from_html(text)
            json = self._json_url_to_dict(oembed_url)

            # Now, let's grab the JSON from that URL.
            cleaned_data["iframe_url"] = self._iframe_url_from_json(json)

        return cleaned_data

    def save(self, commit=True):
        # As embed_code and thumbnail_url are not in the fieldsets of the
        # form, they won't be saved to the new object. But those things
        # will be in cleaned_data, so...
        obj = super(VideoAdminForm, self).save(
            commit=False,
        )

        if obj.external_url:
            obj.iframe_url = self.cleaned_data["iframe_url"]
        else:
            obj.iframe_url = None
        obj.save()
        return obj

    # These little functions do very small data chomping tasks and raise
    # ValidationError if some set of conditions is not true. It helps to
    # reduce the complexity of `clean`.
    def _iframe_url_from_json(self, json):
        if not "html" in json:
            raise forms.ValidationError("Unexpected embed code received from video provider.")

        # We'll assume they've given us something that looks like HTML.
        iframe_parser = IframeFindingParser()
        iframe_parser.feed(json["html"])
        if not iframe_parser.iframe_url:
            raise forms.ValidationError(
                "Unexpected embed code received from video provider."
            )
        return iframe_parser.iframe_url

    def _json_url_to_dict(self, url):
        # Gets JSON from a URL. Raises ValidationError if it fails.
        try:
            req = requests.get(url)
            json = req.json()
        except:
            # Broad exception because a lot of possible errors could
            # happen here. Not just requests.exception.RequestException -
            # there's all the ones that could happen in the json library
            # too.
            raise forms.ValidationError(
                "Unable to get video embed code. If you are sure you "
                "have entered a valid URL, it could be a temporary "
                "server problem."
            )
        return json

    def _oembed_url_from_html(self, text):
        # Try to parse the HTML. Hopefully it looks something like
        # HTML...
        parser = OEmbedFindingParser()
        try:
            parser.feed(text)
        except:
            # HTML that even `html.parser` cannot cope with. Just call
            # this an error and go home.
            raise forms.ValidationError(
                "Unable to parse HTML document. Is the URL valid?"
            )

        if not parser.oembed_url:
            # This can happen if a video is private or deleted.
            raise forms.ValidationError(
                "Unable to get video embed code. Make sure you have "
                "entered a valid URL and that the video is not private."
            )

        return parser.oembed_url
