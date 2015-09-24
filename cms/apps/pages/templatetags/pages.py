"""Template tags used to render pages."""
from __future__ import unicode_literals

from django import template
from django.conf import settings
from django.utils.html import escape

from cms.apps.pages.models import Page
from cms.models import SearchMetaBase

register = template.Library()


# Navigation.

@register.inclusion_tag("pages/navigation.html", takes_context=True)
def navigation(context, pages, section=None):
    """
    Renders a navigation list for the given pages.

    The pages should all be a subclass of PageBase, and possess a get_absolute_url() method.

    You can also specify an alias for the navigation, at which point it will be set in the
    context rather than rendered.
    """
    request = context["request"]
    # Compile the entries.

    def page_entry(page):
        # Do nothing if the page is to be hidden from not logged in users
        if page.hide_from_anonymous and not request.user.is_authenticated():
            return

        url = page.get_absolute_url()

        return {
            "url": url,
            "page": page,
            "title": str(page),
            "here": request.path.startswith(url)
        }

    # All the applicable nav items
    entries = [page_entry(x) for x in pages if page_entry(x) is not None]

    # Add the section.
    if section:
        section_entry = page_entry(section)
        section_entry["here"] = context["pages"].current == section_entry["page"]
        entries = [section_entry] + list(entries)

    # Render the template.
    context.update({
        "request": request,
        "navigation": entries,
    })

    return context


@register.assignment_tag(takes_context=True)
def get_navigation(context, pages, section=None):
    """Returns a navigation list for the given pages."""
    return navigation(context, pages, section)["navigation"]


# Page linking.
@register.simple_tag
def page_url(page, view_func=None, *args, **kwargs):
    """Renders the URL of the given view func in the given page."""
    url = None
    if isinstance(page, int):
        try:
            page = Page.objects.get(pk=page)
        except Page.DoesNotExist:
            url = "#"
            page = None
    if page is None:
        url = "#"
    else:
        # Get the page URL.
        if view_func is None:
            url = page.get_absolute_url()
        else:
            url = page.reverse(view_func, args, kwargs)
    # Return the value, or set as a context variable as appropriate.
    return escape(url)


# Page widgets.

@register.simple_tag(takes_context=True)
def meta_description(context, description=None):
    """
    Renders the content of the meta description tag for the current page::

        {% meta_description %}

    You can override the meta description by setting a context variable called
    'meta_description'::

        {% with "foo" as meta_description %}
            {% meta_description %}
        {% endwith %}

    You can also provide the meta description as an argument to this tag::

        {% meta_description "foo" %}

    """
    if description is None:
        description = context.get("meta_description")
    if description is None:
        request = context["request"]
        page = request.pages.current
        if page:
            description = page.meta_description

    return escape(description or "")


@register.simple_tag(takes_context=True)
def meta_robots(context, index=None, follow=None, archive=None):
    """
    Renders the content of the meta robots tag for the current page::

        {% meta_robots %}

    You can override the meta robots by setting boolean context variables called
    'robots_index', 'robots_archive' and 'robots_follow'::

        {% with 1 as robots_follow %}
            {% meta_robots %}
        {% endwith %}

    You can also provide the meta robots as three boolean arguments to this
    tag in the order 'index', 'follow' and 'archive'::

        {% meta_robots 1 1 1 %}

    """
    # Override with context variables.
    if index is None:
        index = context.get("robots_index")
    if follow is None:
        follow = context.get("robots_follow")
    if archive is None:
        archive = context.get("robots_archive")
    # Final override, set to True.
    if index is None:
        index = True
    if follow is None:
        follow = True
    if archive is None:
        archive = True
    # Generate the meta content.
    robots = ", ".join((
        index and "INDEX" or "NOINDEX",
        follow and "FOLLOW" or "NOFOLLOW",
        archive and "ARCHIVE" or "NOARCHIVE",
    ))
    return escape(robots)


def absolute_domain_url(context):
    request = context['request']

    https = 's' if request.is_secure() else ''

    return 'http{}://{}'.format(
        https,
        settings.SITE_DOMAIN
    )


@register.simple_tag(takes_context=True)
def canonical_url(context):
    request = context['request']

    url = '{}{}'.format(
        absolute_domain_url(context),
        request.path
    )

    return escape(url)


@register.simple_tag(takes_context=True)
def og_title(context, title=None):
    if title is None:
        title = context.get('og_title')

    if title is None or title == '':
        request = context['request']
        page = request.pages.current

        if page:
            title = page.og_title

        if not title:
            title = context.get('title') or (page and page.title) or (page and page.browser_title)

    return escape(title or '')


@register.simple_tag(takes_context=True)
def og_description(context, description=None):
    if description is None:
        description = context.get('og_description')

    if description is None:
        request = context['request']
        page = request.pages.current

        if page:
            description = page.og_description

    return escape(description or '')


@register.simple_tag(takes_context=True)
def og_image(context, image=None):
    image_obj = None

    if image is None:
        image_obj = context.get('og_image')

    if image_obj is None:
        request = context['request']
        page = request.pages.current

        if page:
            image_obj = page.og_image

    if image_obj:
        image = '{}{}'.format(
            absolute_domain_url(context),
            image_obj.get_absolute_url()
        )

    return escape(image or '')


@register.simple_tag(takes_context=True)
def twitter_card(context, card=None):
    choices = dict(SearchMetaBase._meta.get_field('twitter_card').choices)

    # Load from context if exists
    if not card:
        card = context.get('twitter_card')

    # If we are still None, look at page content
    if not card:

        # Get current page from request
        request = context['request']
        current_page = request.pages.current
        homepage = request.pages.homepage

        # Use either the current page twitter card, or the homepage twitter card
        card = current_page.twitter_card or homepage.twitter_card

    if card or card == 0:
        card = str(choices[card]).lower()

    return escape(card or '')


@register.simple_tag(takes_context=True)
def twitter_title(context, title=None):

    # Load from context if exists
    if not title:
        title = context.get('twitter_title')

    # If we are still None, look at page content
    if not title:

        # Get current page from request
        request = context['request']
        current_page = request.pages.current
        homepage = request.pages.homepage

        # Use either the current page twitter title, or the homepage twitter title
        title = current_page.twitter_title or homepage.twitter_title

        # If everything fails, fallback to OG tag title
        if not title:
            title = og_title(context)

    # Return title, or an empty string if nothing is working
    return escape(title or '')


@register.simple_tag(takes_context=True)
def twitter_description(context, description=None):
    # Load from context if exists
    if not description:
        description = context.get('twitter_description')

    # If we are still None, look at page content
    if not description:

        # Get current page from request
        request = context['request']
        current_page = request.pages.current
        homepage = request.pages.homepage

        # Use either the current page twitter description, or the homepage twitter description
        description = current_page.twitter_description or homepage.twitter_description

        # If everything fails, fallback to OG tag title
        if not description:
            description = og_description(context)

    # Return description, or an empty string if nothing is working
    return escape(description or '')


@register.simple_tag(takes_context=True)
def twitter_image(context, image=None):
    # Load from context if exists
    if not image:
        image = context.get('twitter_image')

    # Get current page from request
    request = context['request']

    # If we are still None, look at page content
    if not image:

        current_page = request.pages.current
        homepage = request.pages.homepage

        # Use either the current page twitter image, or the homepage twitter image
        image = current_page.twitter_image or homepage.twitter_image

        # If everything fails, fallback to OG tag title
        if not image:
            image = og_image(context)

    # If its a file object, load the URL manually
    if type(image).__name__ == 'File' and hasattr(request, "META"):
        image = "{}{}".format(
            absolute_domain_url(context),
            image.get_absolute_url()
        )

    # Return image, or an empty string if nothing is working
    return escape(image or '')


@register.inclusion_tag("pages/title.html", takes_context=True)
def title(context, browser_title=None):
    """
    Renders the title of the current page::

        {% title %}

    You can override the title by setting a context variable called 'title'::

        {% with "foo" as title %}
            {% title %}
        {% endwith %}

    You can also provide the title as an argument to this tag::

        {% title "foo" %}

    """
    request = context["request"]
    page = request.pages.current
    homepage = request.pages.homepage
    # Render the title template.
    return {
        "title": browser_title or context.get("title") or (page and page.browser_title) or (page and page.title) or "",
        "site_title": (homepage and homepage.browser_title) or (homepage and homepage.title) or ""
    }


@register.inclusion_tag("pages/breadcrumbs.html", takes_context=True)
def breadcrumbs(context, page=None, extended=False):
    """
    Renders the breadcrumbs trail for the current page::

        {% breadcrumbs %}

    To override and extend the breadcrumb trail within page applications, add
    the 'extended' flag to the tag and add your own breadcrumbs underneath::

        {% breadcrumbs extended=1 %}

    """
    request = context["request"]
    # Render the tag.
    page = page or request.pages.current
    if page:
        breadcrumb_list = [{
            "short_title": breadcrumb.short_title or breadcrumb.title,
            "title": breadcrumb.title,
            "url": breadcrumb.get_absolute_url(),
            "last": False,
            "page": breadcrumb,
        } for breadcrumb in request.pages.breadcrumbs]
    else:
        breadcrumb_list = []
    if not extended:
        breadcrumb_list[-1]["last"] = True
    # Render the breadcrumbs.
    return {
        "breadcrumbs": breadcrumb_list,
    }


@register.inclusion_tag("pages/header.html", takes_context=True)
def header(context, page_header=None):
    """
    Renders the header for the current page::

        {% header %}

    You can override the page header by providing a 'header' or 'title' context
    variable. If both are present, then 'header' overrides 'title'::

        {% with "foo" as header %}
            {% header %}
        {% endwith %}

    You can also provide the header as an argument to this tag::

        {% header "foo" %}

    """
    request = context["request"]
    page_header = page_header or context.get("header") or context.get("title") or request.pages.current.title
    return {
        "header": page_header,
    }


@register.simple_tag(takes_context=True)
def country_code(context):
    if hasattr(context.request, 'country') and context.request.country:
        return '/{}'.format(
            context.request.country.code.lower()
        )
    return ''
