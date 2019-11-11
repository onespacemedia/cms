'''Views used by the links application.'''

from django.shortcuts import redirect


def index(request):
    '''Redirects to a new page.'''
    content = request.pages.current.content
    return redirect(
        content.get_link_url_resolved(),
        permanent=content.permanent
    )
