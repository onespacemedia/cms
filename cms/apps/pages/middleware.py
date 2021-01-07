'''Custom middleware used by the pages application.'''
import re

from django.conf import settings
from django.db.models import Q
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import redirect
from django.urls import resolve, is_valid_path
from django.utils.http import escape_leading_slashes
from django.utils.functional import cached_property

from .models import Page, Country
from .views import PageDispatcherView

if 'cms.middleware.LocalisationMiddleware' in settings.MIDDLEWARE:
    from django.contrib.gis.geoip2 import GeoIP2
    from geoip2.errors import AddressNotFoundError


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


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
    def navigation(self):
        return self.homepage.navigation

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

                    urlconf = getattr(page.content, 'urlconf', None) if hasattr(page, 'content') else None

                    # Check if the URL with a slash appended is resolved by the current page's urlconf
                    if (is_valid_path(path_info, urlconf)
                            or not is_valid_path(f'{path_info}/', urlconf)):
                        # Check if the URL with a slash appended resolves for something other than a page
                        match = resolve(f'{path_info}/', getattr(request, 'urlconf', None))
                        if getattr(match.func, 'view_class', None) is PageDispatcherView:
                            # Couldn't find any view that would be resolved for this URL
                            # No point redirecting to a URL that will 404
                            return None

                new_path = request.get_full_path(force_append_slash=True)
                # Prevent construction of scheme relative urls.
                new_path = escape_leading_slashes(new_path)

                return HttpResponsePermanentRedirect(new_path)


class LocalisationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.exclude_urls = [
            re.compile(url_regex) for url_regex in getattr(settings, 'LOCALISATION_MIDDLEWARE_EXCLUDE_URLS', ())
        ]

    def __call__(self, request, geoip_path=None):
        # Continue for media and admin
        if any(map(lambda pattern: pattern.match(request.path_info[1:]), self.exclude_urls)):
            return self.get_response(request)

        # Set a default country object
        request.country = None

        # Check to see if we have a country in the URL
        country_match = re.match('/([a-z]{2})/|\b', request.path)
        if country_match:

            # Try and get a country from the database
            try:
                request.country = Country.objects.get(
                    code__iexact=str(country_match.group(1))
                )

                request.path = request.path.replace('/{}'.format(
                    country_match.group(1)
                ), '')
                request.path_info = request.path

            except Country.DoesNotExist:
                pass

        # If we don't have a country at this point, we need to do some ip
        # checking or assumption
        if request.country is None:
            # Get the Geo location of the requests IP
            geo_ip = GeoIP2(path=geoip_path)

            try:
                country_geo_ip = geo_ip.country(get_client_ip(request))
            except AddressNotFoundError:
                # If there's no county found for that IP, just don't look for a country
                # and go with the default
                country_geo_ip = {}

            code = country_geo_ip.get('country_code', '')

            request.country = Country.objects.filter(
                Q(code__iexact=code) | Q(default=True)
            ).order_by('-default').first()

            if request.country:
                return redirect('/{}{}'.format(
                    request.country.code.lower(),
                    request.path,
                ))

        response = self.get_response(request)

        return response
