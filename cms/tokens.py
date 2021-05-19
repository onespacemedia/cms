import hmac

from django.conf import settings
from django.utils.crypto import salted_hmac
from django.utils.encoding import force_bytes


class PreviewTokenGenerator:
    key_salt = "PreviewTokenGenerator"
    secret = None

    def __init__(self, url):
        self.url = url
        self.secret = self.secret or settings.SECRET_KEY

    def verify(self, token):
        return hmac.compare_digest(force_bytes(self.make_token()), force_bytes(token))

    def make_token(self):
        hash_string = salted_hmac(
            self.key_salt,
            self._make_hash_value(),
            secret=self.secret,
        ).hexdigest()[::2]  # Limit to shorten the URL.
        return hash_string

    def _make_hash_value(self):
        return self.url
