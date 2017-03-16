"""Views used by the CMS."""

from django.shortcuts import render
from django.views import generic
from django.views.decorators.cache import cache_page


def handler500(request):
    """Renders a pretty error page."""
    response = render(request, "500.html", {})
    response.status_code = 500
    return response


class TextTemplateView(generic.TemplateView):

    """A template view that returns a text/plain response."""

    content_type = "text/plain; charset=utf-8"

    def render_to_response(self, context, **kwargs):
        """Dispatches the request."""
        kwargs.setdefault("content_type", self.content_type)
        return super(TextTemplateView, self).render_to_response(context, **kwargs)


class SearchMetaDetailMixin(object):

    """Generates the context for an search meta detail page."""

    def get_context_data(self, **kwargs):
        """Adds in the additional search meta context data."""
        context = super(SearchMetaDetailMixin, self).get_context_data(**kwargs)
        defaults = self.object.get_context_data()
        defaults.update(context)
        return defaults


class PageDetailMixin(SearchMetaDetailMixin):

    """Generates the context for a page detail view."""


class SearchMetaDetailView(SearchMetaDetailMixin, generic.DetailView):

    """A simple entity detail view."""


class PageDetailView(PageDetailMixin, generic.DetailView):

    """A simple page detail view."""


class CacheMixin(object):
    cache_timeout = 60

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        if hasattr(self.request, 'user') and self.request.user.is_authenticated():
            return super(CacheMixin, self).dispatch(*args, **kwargs)

        return cache_page(self.get_cache_timeout())(super(CacheMixin, self).dispatch)(*args, **kwargs)
