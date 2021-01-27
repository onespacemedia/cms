'''Custom middleware used by the pages application.'''

import re

from django.conf import settings
from django.shortcuts import redirect
from django.template.response import SimpleTemplateResponse
from django.utils.deprecation import MiddlewareMixin

from cms.apps.pages.models import Country
from cms.models import PublicationManagementError, publication_manager, path_token_generator


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class PublicationMiddleware(MiddlewareMixin):

    '''Middleware that enables preview mode for admin users.'''

    def process_request(self, request):
        '''Starts preview mode, if available.'''

        exclude_urls = [
            re.compile(url)
            for url in
            getattr(settings, 'PUBLICATION_MIDDLEWARE_EXCLUDE_URLS', ())
        ]

        if not any(pattern.match(request.path_info[1:]) for pattern in exclude_urls):
            # See if preview mode is requested.
            try:
                path = f'{request.path_info[1:] if request.path_info[1:] else request.path_info}'
                # Check for the value of 'preview' matching the token for the
                # current path. This is intended to throw KeyError if is not
                # present.
                token_preview_valid = path_token_generator.check_token(request.GET['preview'], path)
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

    def process_response(self, request, response):
        '''Cleans up after preview mode.'''
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


class LocalisationMiddleware(MiddlewareMixin):

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
                request.country = Country.objects.get(
                    code__iexact=str(country_match.group(1))
                )

                request.path = request.path.replace('/{}'.format(
                    country_match.group(1)
                ), '')
                request.path_info = request.path

            except Country.DoesNotExist:
                pass

    def process_response(self, request, response, geoip_path=None):
        # This import is here to avoid an exception being thrown when
        # localisation is not required - this import will fail if GeoIP files
        # are not present.
        from django.contrib.gis.geoip2 import GeoIP2
        from geoip2.errors import AddressNotFoundError

        # Continue for media
        if request.path.startswith('/media/') \
           or request.path.startswith('/admin/') \
           or request.path.startswith('/social-auth/'):
            return response

        # If we don't have a country at this point, we need to do some ip
        # checking or assumption
        if request.country is None:

            # Get the Geo location of the requests IP
            geo_ip = GeoIP2(path=geoip_path)

            try:
                country_geo_ip = geo_ip.country(get_client_ip(request))
            except AddressNotFoundError:
                # If no county found for that IP, just don't look for a country
                # and go with the default
                country_geo_ip = {}

            if country_geo_ip.get('country_code'):
                try:
                    request.country = Country.objects.get(
                        code__iexact=country_geo_ip['country_code']
                    )
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
