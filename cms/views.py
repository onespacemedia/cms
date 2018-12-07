'''Views used by the CMS.'''

from django.shortcuts import render
from django.views import generic


def handler500(request):
    '''Renders a pretty error page.'''
    response = render(request, '500.html', {})
    response.status_code = 500
    return response


class TextTemplateView(generic.TemplateView):
    '''A template view that returns a text/plain response.'''

    content_type = 'text/plain; charset=utf-8'

    def render_to_response(self, context, **kwargs):
        '''Dispatches the request.'''
        kwargs.setdefault('content_type', self.content_type)
        return super().render_to_response(context, **kwargs)


class SearchMetaDetailMixin:
    '''Generates the context for objects that inherit from SearchMetaBase.'''

    def get_context_data(self, **kwargs):
        '''Adds in the additional search meta context data.'''
        context = super().get_context_data(**kwargs)
        defaults = self.object.get_context_data()
        defaults.update(context)
        return defaults


class PageDetailMixin(SearchMetaDetailMixin):
    '''Generates the context for derivatives of PageBase.'''


class SearchMetaDetailView(SearchMetaDetailMixin, generic.DetailView):
    '''A simple entity detail view for SearchMetaBase derivatives.'''


class PageDetailView(PageDetailMixin, generic.DetailView):
    '''A simple detail view for PageBase derivatives.'''
