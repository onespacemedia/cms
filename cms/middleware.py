"""Custom middleware used by the pages application."""

import re

from django.conf import settings
from django.shortcuts import redirect
from django.template.response import SimpleTemplateResponse
from django.contrib.gis.geoip import GeoIP

from cms.apps.pages.models import Country
from cms.models import publication_manager, PublicationManagementError


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class PublicationMiddleware(object):

    """Middleware that enables preview mode for admin users."""

    def __init__(self):
        """Initializes the PublicationMiddleware."""
        self.exclude_urls = [
            re.compile(url)
            for url in
            getattr(settings, "PUBLICATION_MIDDLEWARE_EXCLUDE_URLS", ())
        ]

    def process_request(self, request):
        """Starts preview mode, if available."""
        if not any(pattern.match(request.path_info[1:]) for pattern in self.exclude_urls):
            # See if preview mode is requested.
            try:
                preview_mode = bool(int(request.GET.get("preview", 0)))
            except ValueError:
                preview_mode = False
            # Only allow preview mode if the user is a logged in administrator.
            preview_mode = preview_mode and request.user.is_authenticated() and request.user.is_staff and request.user.is_active
            publication_manager.begin(not preview_mode)

    def process_response(self, request, response):
        """Cleans up after preview mode."""
        # Render the response if we're in a block of publication management.
        if publication_manager.select_published_active():
            if isinstance(response, SimpleTemplateResponse):
                response = response.render()
        # Clean up all blocks.
        while True:
            try:
                publication_manager.end()
            except PublicationManagementError:
                break
        # Carry on as normal.
        return response


class LocalisationMiddleware(object):

    def process_request(self, request):

        # request.path = '/news/'
        # request.path_info = '/news/'
        # request.country = 'france'

        # Continue for media
        if request.path.startswith('/media/') \
                or request.path.startswith('/admin/') \
                or request.path.startswith('/social-auth/'):
            return None

        # Set a default country object
        request.country = None

        # Check to see if we have a country in the URL
        country_match = re.match('/([a-z]{2})/|\b', request.path)
        if country_match:

            # Try and get a country from the database
            try:
                request.country = Country.objects.get(code=str(country_match.group(1)).upper())

                request.path = request.path.replace('/{}'.format(
                    country_match.group(1)
                ), '')
                request.path_info = request.path

            except Country.DoesNotExist:
                pass

    def process_response(self, request, response):

        # Continue for media
        if request.path.startswith('/media/') \
           or request.path.startswith('/admin/') \
           or request.path.startswith('/social-auth/'):
            return response

        # If we don't have a country at this point, we need to do some ip
        # checking or assumption
        if request.country is None:

            # Get the Geo location of the requests IP
            geo_ip = GeoIP()
            country_geo_ip = geo_ip.country(get_client_ip(request))

            if country_geo_ip['country_code']:
                try:
                    request.country = Country.objects.get(
                        code=country_geo_ip['country_code'])
                except Country.DoesNotExist:
                    pass

            # Try and get the default
            if request.country is None:
                try:
                    request.country = Country.objects.get(default=True)
                except Country.DoesNotExist:
                    pass

            if request.country:
                return redirect('/{}{}'.format(
                    request.country.code.lower(),
                    request.path
                ))

        return response
