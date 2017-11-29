"""Custom middleware used by the pages application."""

import sys

from django.conf import settings
from django.core import urlresolvers
from django.core.handlers.base import BaseHandler
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import SimpleTemplateResponse
from django.utils.functional import cached_property
from django.views.debug import technical_404_response

from cms.apps.pages.models import Page


class RequestPageManager(object):

    """Handles loading page objects."""

    def __init__(self, request):
        """Initializes the RequestPageManager."""
        self._request = request
        self._path = self._request.path
        self._path_info = self._request.path_info

    @cached_property
    def homepage(self):
        """Returns the site homepage."""
        try:
            return Page.objects.get_homepage()
        except Page.DoesNotExist:
            return None

    @property
    def is_homepage(self):
        """Whether the current request is for the site homepage."""
        return self._path == self.homepage.get_absolute_url()

    @property
    def section(self):
        """The current primary level section, or None."""
        try:
            page = self.breadcrumbs[1]
            return self.alternate_page_version(page)
        except IndexError:
            return None

    @property
    def subsection(self):
        """The current secondary level section, or None."""
        try:
            page = self.breadcrumbs[2]
            return self.alternate_page_version(page)
        except IndexError:
            return None

    @property
    def current(self):
        """The current best-matched page."""
        try:
            page = self.breadcrumbs[-1]
            return self.alternate_page_version(page)
        except IndexError:
            return None

    @property
    def is_exact(self):
        """Whether the current page exactly matches the request URL."""
        return self.current.get_absolute_url() == self._path
