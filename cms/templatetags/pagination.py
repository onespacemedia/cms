"""Template tags for rendering pagination."""
from __future__ import unicode_literals

import jinja2

from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.utils.html import escape
from django_jinja import library


@library.global_function
@jinja2.contextfunction
def paginate(context, queryset, per_page=10, key="page"):
    """Paginates the given queryset as sets it in the context as a variable."""
    request = context["request"]

    # Parse the page number.
    try:
        page_number = int(request.GET[key])
    except (KeyError, TypeError, ValueError):
        page_number = 1
    # Create the paginator.
    try:
        page = Paginator(queryset, per_page).page(page_number)
    except InvalidPage:
        raise Http404("There are no items on page {}.".format(page_number))
    page._pagination_key = key

    return page


@library.global_function
@library.render_with('pagination/pagination.html')
@jinja2.contextfunction
def render_pagination(context, page_obj, pagination_key=None):
    """Renders the pagination for the given page of items."""
    return {
        "request": context["request"],
        "page_obj": page_obj,
        "paginator": page_obj.paginator,
        "pagination_key": pagination_key or getattr(page_obj, "_pagination_key", "page")
    }


@library.global_function
@jinja2.contextfunction
def get_pagination_url(context, page_number):
    """Renders the URL for the given page number."""
    request = context["request"]
    url = request.path
    params = request.GET.copy()
    if str(page_number) != "1":
        params[context.get("pagination_key", "page")] = page_number
    else:
        params.pop(context.get("pagination_key", "page"), None)
    if params:
        url += "?%s" % params.urlencode()
    return escape(url)
