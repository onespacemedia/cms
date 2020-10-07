'''Custom middleware used by the pages application.'''

import sys

from django.conf import settings
from django.urls import is_valid_path
from django.core.handlers.exception import handle_uncaught_exception
from django.http import Http404, HttpResponsePermanentRedirect
from django.utils.http import escape_leading_slashes
from django.shortcuts import redirect
from django.template.response import SimpleTemplateResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import cached_property
from django.views.debug import technical_404_response

from cms.apps.pages.models import Page


class RequestPageManager:

    '''Handles loading page objects.'''

    def __init__(self, request):
        '''Initializes the RequestPageManager.'''
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
        # Save ourselves a DB query if we are not using localisation.
        if not self.country:
            return page

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
        '''Returns the site homepage.'''
        try:
            return Page.objects.get_homepage()
        except Page.DoesNotExist:
            return None

    @cached_property
    def is_homepage(self):
        '''Whether the current request is for the site homepage.'''
        return self._path == self.homepage.get_absolute_url()

    @cached_property
    def breadcrumbs(self):
        '''The breadcrumbs for the current request.'''
        breadcrumbs = []
        slugs = self._path_info.strip('/').split('/')
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

    @cached_property
    def section(self):
        '''The current primary level section, or None.'''
        try:
            page = self.breadcrumbs[1]
            return self.alternate_page_version(page)
        except IndexError:
            return None

    @cached_property
    def subsection(self):
        '''The current secondary level section, or None.'''
        try:
            page = self.breadcrumbs[2]
            return self.alternate_page_version(page)
        except IndexError:
            return None

    @cached_property
    def current(self):
        '''The current best-matched page.'''
        try:
            page = self.breadcrumbs[-1]
            return self.alternate_page_version(page)
        except IndexError:
            return None

    @cached_property
    def is_exact(self):
        '''Whether the current page exactly matches the request URL.'''
        return self.current.get_absolute_url() == self._path

    @cached_property
    def current_path(self):
        '''The URL to be checked against the page's urlconf.'''
        script_name = self.current.get_absolute_url()[:-1]
        return self._path[len(script_name):]


class PageMiddleware:
    '''
    Middleware necessary for the use of the pages app

        - Adds 'pages' to the request

        - Rewrites the URL based on APPEND_SLASH in the case of PageView raising a Http404 exception
    '''
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.pages = RequestPageManager(request)

        response = self.get_response(request)

        return response

    def process_exception(self, request, exception):
        '''Rewrite the URL based on settings.APPEND_SLASH and the urlconf of the current page.'''

        if isinstance(exception, Http404):
            if settings.APPEND_SLASH and not request.path_info.endswith('/'):
                page = request.pages.current

                if page:
                    script_name = page.get_absolute_url()[:-1]
                    path_info = request.path[len(script_name):]

                    if (is_valid_path(path_info, page.content.urlconf)
                            or not is_valid_path(f'{path_info}/', page.content.urlconf)):
                        return None

                new_path = request.get_full_path(force_append_slash=True)
                # Prevent construction of scheme relative urls.
                new_path = escape_leading_slashes(new_path)

                return HttpResponsePermanentRedirect(new_path)
