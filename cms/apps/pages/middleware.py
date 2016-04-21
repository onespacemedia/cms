"""Custom middleware used by the pages application."""
import re
import sys

from cms.apps.pages.models import Page
from django.conf import settings
from django.core import urlresolvers
from django.core.handlers.base import BaseHandler
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import SimpleTemplateResponse
from django.utils.functional import cached_property
from django.views.debug import technical_404_response
from threadlocals.threadlocals import get_current_request

from .models import get_registered_content, LANGUAGES


class RequestPageManager(object):

    """Handles loading page objects."""

    def __init__(self, request):
        """Initializes the RequestPageManager."""

        # Does the current path start with a language code?
        code_test = re.match(r'^\/({})\/'.format('|'.join([
            x[0] for x in LANGUAGES
        ])), request.path)

        if code_test:
            request.language = code_test.group(1)
            request.path = re.sub(r'^/{}'.format(request.language), '', request.path)
            request.path_info = re.sub(r'^/{}'.format(request.language), '', request.path_info)
        else:
            # We need to redirect.
            request.language = None

        # Get the available languages and tack them onto the request too.
        languages = []

        for model in get_registered_content():
            languages.extend(model.objects.exclude(
                language__in=languages,
            ).distinct('language').values_list('language', flat=True))

        request.languages = languages
        request.languages = [
            (x[0], x[1][1])
            for x in LANGUAGES
            if x[0] in languages
        ]

        self._request = request
        self._path = self._request.path
        self._path_info = self._request.path_info

    @cached_property
    def homepage(self):
        """Returns the site homepage."""
        try:
            return Page.objects.root_nodes()[0]
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

                children = page.get_descendants(include_self=True)

                for child in children:
                    if child.content is None:
                        continue

                    if child.slug == slug:
                        do_breadcrumbs(child)
                        break
                    pass

        if self.homepage:
            do_breadcrumbs(self.homepage)

        return breadcrumbs

    @property
    def section(self):
        """The current primary level section, or None."""
        try:
            return self.breadcrumbs[1]
        except IndexError:
            return None

    @property
    def subsection(self):
        """The current secondary level section, or None."""
        try:
            return self.breadcrumbs[2]
        except IndexError:
            return None

    @property
    def current(self):
        """The current best-matched page."""
        try:
            page = self.breadcrumbs[-1]
            return page
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

    def process_response(self, request, response):
        """If the response was a 404, attempt to serve up a page."""
        if response.status_code != 404:
            return response

        if not request.language:
            # Redirect to the default language.
            return redirect('/en{}'.format(request.path), permanent=False)

        # Get the current page.
        page = request.pages.current
        if page is None:
            return response

        script_name = page.content.get_absolute_url()[:-1]
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
                if path_info == '':
                    path_info = '/'

                callback, callback_args, callback_kwargs = urlresolvers.resolve(path_info, page.content.urlconf)
            except urlresolvers.Resolver404:
                # First of all see if adding a slash will help matters.
                if settings.APPEND_SLASH:
                    new_path_info = path_info + "/"

                    try:
                        urlresolvers.resolve(new_path_info, page.content.urlconf)
                        return redirect(script_name + new_path_info, permanent=True)
                    except urlresolvers.Resolver404:
                        pass
                return response
            response = callback(request, *callback_args, **callback_kwargs)
            # Validate the response.
            if not response:
                raise ValueError("The view {0!r} didn't return an HttpResponse object.".format(
                    callback.__name__
                ))

            if request:
                if page.content.auth_required() and not request.user.is_authenticated():
                    return redirect("{}?next={}".format(
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
            return BaseHandler().handle_uncaught_exception(request, urlresolvers.get_resolver(None), sys.exc_info())
