'''Custom middleware used by the pages application.'''

import sys

from django.conf import settings
from django import urls
from django.core.handlers.exception import handle_uncaught_exception
from django.http import Http404
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


class PageMiddleware(MiddlewareMixin):

    '''Serves up pages when no other view is matched.'''

    def process_request(self, request):
        '''Annotates the request with a page manager.'''
        request.pages = RequestPageManager(request)

    def process_response(self, request, response):
        '''If the response was a 404, attempt to serve up a page.'''
        if response.status_code != 404:
            return response
        # Get the current page.
        page = request.pages.current
        if page is None:
            return response
        script_name = page.get_absolute_url()[:-1]
        path_info = request.path[len(script_name):]

        # Continue for media
        if request.path.startswith('/media/'):
            return response

        if hasattr(request, 'country') and request.country is not None:
            script_name = '/{}{}'.format(
                request.country.code.lower(),
                script_name
            )

        # Dispatch to the content.
        try:
            try:
                callback, callback_args, callback_kwargs = urls.resolve(path_info, page.content.urlconf)
            except urls.Resolver404:
                # First of all see if adding a slash will help matters.
                if settings.APPEND_SLASH:
                    new_path_info = path_info + '/'

                    try:
                        urls.resolve(new_path_info, page.content.urlconf)
                    except urls.Resolver404:
                        pass
                    else:
                        return redirect(script_name + new_path_info, permanent=True)
                return response
            response = callback(request, *callback_args, **callback_kwargs)
            # Validate the response.
            if not response:
                raise ValueError("The view {0!r} didn't return an HttpResponse object.".format(
                    callback.__name__
                ))

            if request:
                if page.auth_required() and not request.user.is_authenticated():
                    return redirect('{}?next={}'.format(
                        settings.LOGIN_URL,
                        request.path
                    ))

            if isinstance(response, SimpleTemplateResponse):
                return response.render()

            return response
        except Http404 as ex:
            if settings.DEBUG:
                return technical_404_response(request, ex)
            # Let the normal 404 mechanisms render an error page.
            return response
        except:
            return handle_uncaught_exception(request, urls.get_resolver(None), sys.exc_info())
