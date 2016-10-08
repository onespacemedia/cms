"""Custom middleware used by the pages application."""

import sys

from django.conf import settings
from django.core import urlresolvers
from django.core.handlers.base import BaseHandler
from django.http import Http404
from django.views.debug import technical_404_response
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.template.response import SimpleTemplateResponse

from cms.apps.pages.models import Page


class RequestPageManager(object):

    """Handles loading page objects."""

    def __init__(self, request):
        """Initializes the RequestPageManager."""
        self._request = request
        self._path = self._request.path
        self._path_info = self._request.path_info

    @cached_property
    def country(self):
        if hasattr(self._request, 'country'):
            return self._request.country
        return None

    def request_country_group(self):
        if hasattr(self._request, 'country'):
            if self._request.country:
                return self._request.country.group

        return None

    def alternate_page_version(self, page):

        try:
            # See if the page has any alternate versions for the current country
            alternate_version = Page.objects.get(
                is_content_object=True,
                owner=page,
                country_group=self.request_country_group()
            )

            return alternate_version

        except:
            return page

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

    @cached_property
    def breadcrumbs(self):
        """The breadcrumbs for the current request."""
        breadcrumbs = []
        slugs = self._path_info.strip("/").split("/")
        slugs.reverse()

        def do_breadcrumbs(page):
            breadcrumbs.append(page)
            if slugs:
                slug = slugs.pop()
                for child in page.children:
                    if child.slug == slug:
                        do_breadcrumbs(child)
                        break
        if self.homepage:
            do_breadcrumbs(self.homepage)
        return breadcrumbs

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


class PageMiddleware(object):

    """Serves up pages when no other view is matched."""

    def process_request(self, request):
        """Annotates the request with a page manager."""
        request.pages = RequestPageManager(request)
