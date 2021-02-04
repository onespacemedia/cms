'''Custom middleware used by the pages application.'''

import re

from django.conf import settings

from cms.tokens import PreviewTokenGenerator
from .models import publication_manager

if 'cms.middleware.LocalisationMiddleware' in settings.MIDDLEWARE:
    from .apps.pages.middleware import LocalisationMiddleware

if 'cms.middleware.VersionMiddleware' in settings.MIDDLEWARE:
    from .apps.pages.middleware import VersionMiddleware


class PublicationMiddleware:

    '''Middleware that enables the preview mode for admin users.'''

    def __init__(self, get_response):
        self.get_response = get_response
        self.exclude_urls = [
            re.compile(url_regex) for url_regex in getattr(settings, 'PUBLICATION_MIDDLEWARE_EXCLUDE_URLS', ())
        ]

    def __call__(self, request):
        if any(map(lambda pattern: pattern.match(request.path_info[1:]), self.exclude_urls)):
            return self.get_response(request)

        # See if preview mode is requested.
        try:
            path = request.path_info
            # Check for the value of 'preview' matching the token for the
            # current path. This is intended to throw KeyError if is not
            # present.
            token = request.GET.get('preview')
            token_generator = PreviewTokenGenerator(path)
            token_preview_valid = token_generator.verify(token)
            # Allow something like preview=1, preview=any_other_value if
            # they are a staff user.
            user_preview = request.GET['preview'] and request.user.is_staff
        except KeyError:
            # Preview mode was not requested.
            user_preview = False
            token_preview_valid = False

        # Only allow preview mode if the user is a logged in administrator
        # or they have a token for this specific path.
        preview_mode = token_preview_valid or user_preview
        publication_manager.begin(not preview_mode)

        request.preview_mode = preview_mode

        response = self.get_response(request)

        publication_manager.end_all()

        # Carry on as normal.
        return response

