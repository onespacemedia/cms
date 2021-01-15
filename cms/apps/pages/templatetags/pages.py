'''Template tags used to render pages.'''
import jinja2
from django import template
from django.conf import settings
from django.utils.html import escape
from django_jinja import library
from jinja2.filters import do_striptags

from cms.apps.pages.models import Page
from cms.models import SearchMetaBase
from cms.templatetags.html import truncate_paragraphs

register = template.Library()


# Navigation.
def _navigation_entries(context, pages, section=None, is_json=False):
    request = context['request']
    # Compile the entries.

    def page_entry(page):
        # Do nothing if the page is to be hidden from not logged in users
        if page.hide_from_anonymous and not request.user.is_authenticated:
            return

        url = page.get_absolute_url()

        if is_json:
            return {
                'url': url,
                'title': str(page),
                'here': request.path.startswith(url),
                'children': [page_entry(x) for x in page.navigation if
                             page is not request.pages.homepage]
            }
        return {
            'url': url,
            'page': page,
            'title': str(page),
            'here': request.path.startswith(url),
            'children': [page_entry(x) for x in page.navigation if page is not request.pages.homepage]
        }

    # All the applicable nav items
    entries = [page_entry(x) for x in pages if page_entry(x) is not None]

    # Add the section.
    if section:
        section_entry = page_entry(section)
        section_entry['here'] = context['pages'].current == section_entry['page']
        entries = [section_entry] + list(entries)

    return entries


@library.global_function
@library.render_with('pages/navigation.html')
@jinja2.contextfunction
def render_navigation(context, pages, section=None):
    '''
    Renders a navigation list for the given pages.

    The pages should all be a subclass of PageBase, and possess a get_absolute_url() method.

    You can also specify an alias for the navigation, at which point it will be set in the
    context rather than rendered.
    '''
    return {
        'navigation': _navigation_entries(context, pages, section),
    }


# Page linking.
@library.global_function
def get_page_url(page, view_func=None, *args, **kwargs):
    '''Renders the URL of the given view func in the given page.'''
    url = None
    if isinstance(page, int):
        try:
            page = Page.objects.get(pk=page)
        except Page.DoesNotExist:
            url = '#'
            page = None
    if page is None:
        url = '#'
    else:
        # Get the page URL.
        if view_func is None:
            url = page.get_absolute_url()
        else:
            url = page.reverse(view_func, args, kwargs)
    # Return the value, or set as a context variable as appropriate.
    return escape(url)


# Page widgets.
@library.global_function
@jinja2.contextfunction
def get_meta_description(context, description=None):
    '''
    Renders the content of the meta description tag for the current page::

        {{ get_meta_description() }}

    You can override the meta description by setting a context variable called
    'meta_description'::

        {% with meta_description = 'foo' %}
            {{ get_meta_description() }}
        {% endwith %}

    You can also provide the meta description as an argument to this tag::

        {{ get_meta_description('foo') %}

    '''
    if description is None:
        description = context.get('meta_description')

    # TODO: Check in the context for objects for every templatetag like this
    if description is None:
        request = context['request']
        page = request.pages.current

        if page:
            description = page.meta_description

    return escape(description or '')


@library.global_function
@jinja2.contextfunction
def get_meta_robots(context, index=None, follow=None, archive=None):
    '''
    Renders the content of the meta robots tag for the current page::

        {{ get_meta_robots() }}

    You can override the meta robots by setting boolean context variables called
    'robots_index', 'robots_archive' and 'robots_follow'::

        {% with robots_follow = 1 %}
            {% get_meta_robots() %}
        {% endwith %}

    You can also provide the meta robots as three boolean arguments to this
    tag in the order 'index', 'follow' and 'archive'::

        {% get_meta_robots(1, 1, 1) %}
    '''
    # Override with context variables.
    if index is None:
        index = context.get('robots_index')
    if follow is None:
        follow = context.get('robots_follow')
    if archive is None:
        archive = context.get('robots_archive')

    # Try to get the values from the current page.
    page = context['pages'].current

    if page:
        if index is None:
            index = page.robots_index
        if follow is None:
            follow = page.robots_follow
        if archive is None:
            archive = page.robots_archive

    # Final override, set to True.
    if index is None:
        index = True
    if follow is None:
        follow = True
    if archive is None:
        archive = True

    # Generate the meta content.
    robots = ', '.join((
        index and 'INDEX' or 'NOINDEX',
        follow and 'FOLLOW' or 'NOFOLLOW',
        archive and 'ARCHIVE' or 'NOARCHIVE',
    ))
    return escape(robots)


def absolute_domain_url(context):
    request = context['request']

    return 'http{}://{}{}'.format(
        's' if request.is_secure() else '',
        'www.' if settings.PREPEND_WWW else '',
        settings.SITE_DOMAIN,
    )


@library.global_function
@jinja2.contextfunction
def get_canonical_url(context):
    '''
    Returns the canonical URL of the current page.
    '''
    request = context['request']

    url = '{}{}'.format(
        absolute_domain_url(context),
        request.path
    )

    return escape(url)


@library.global_function
@jinja2.contextfunction
def get_og_title(context, title=None):
    if not title:
        obj = context.get('object', None)

        if obj:
            title = getattr(obj, 'og_title', None) or getattr(obj, 'title', None)

    if not title:
        title = context.get('og_title')

    if not title or title == '':
        request = context['request']
        page = request.pages.current

        if page:
            title = page.og_title

        if not title:
            title = context.get('title') or (page and page.title) or (page and page.browser_title)

    return escape(title or '')


@library.global_function
@jinja2.contextfunction
def get_og_description(context, description=None):
    if not description:
        description = context.get('og_description')

    if not description:
        obj = context.get('object', None)

        if obj:
            field = getattr(obj, 'description', None) or getattr(obj, 'summary', None)

            description = do_striptags(truncate_paragraphs(field, 1)) if field else None

    if not description:
        request = context['request']
        page = request.pages.current

        if page:
            description = page.og_description

    return escape(description or '')


@library.global_function
@jinja2.contextfunction
def get_og_image(context, image=None):
    image_obj = None

    if not image:
        image_obj = context.get('og_image')

    if not image and not image_obj:
        obj = context.get('object')

        if obj:
            field = getattr(obj, 'image', None) or getattr(obj, 'photo', None) or getattr(obj, 'logo', None)

            image_obj = field if field else None

    if not image_obj:
        request = context['request']
        page = request.pages.current

        if page:
            image_obj = page.og_image

    if image_obj:
        return '{}{}'.format(
            absolute_domain_url(context),
            image_obj.get_absolute_url()
        )

    if image:
        return '{}{}'.format(
            absolute_domain_url(context),
            image.get_absolute_url()
        )

    return None


@library.global_function
@jinja2.contextfunction
def get_twitter_card(context, card=None):
    choices = dict(SearchMetaBase._meta.get_field('twitter_card').choices)

    # To avoid writing custom migrations for every project, use these values rather
    # than updating twitter_card field choices, I know this is a little hacky but it
    # saves a world of migration pain. Could be fixed in next major release.
    card_types_map = {
        0: 'summary',
        1: 'photo',
        2: 'video',
        3: 'product',
        4: 'app',
        5: 'gallery',
        6: 'summary_large_image',
    }

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
        if current_page:
            card = current_page.twitter_card

        if not card and homepage:
            card = homepage.twitter_card

    if card or card == 0:
        card = card_types_map[card]

    return escape(card or card_types_map[0])


@library.global_function
@jinja2.contextfunction
def get_twitter_title(context, title=None):
    # Load from context if exists
    if not title:
        title = context.get('twitter_title')

    # Check the object if we still have nothing
    if not title:
        obj = context.get('object', None)

        if obj:
            title = getattr(obj, 'twitter_title', None) or getattr(obj, 'title', None)

    # If we are still None, look at page content
    if not title:
        # Get current page from request
        request = context['request']
        current_page = request.pages.current
        homepage = request.pages.homepage

        # Use either the current page twitter title, or the homepage twitter title
        if current_page:
            title = current_page.twitter_title

        if not title and homepage:
            title = homepage.twitter_title

        # If everything fails, fallback to OG tag title
        if not title:
            title = get_og_title(context)

    # Return title, or an empty string if nothing is working
    return escape(title or '')


@library.global_function
@jinja2.contextfunction
def get_twitter_description(context, description=None):
    # Load from context if exists
    if not description:
        description = context.get('twitter_description')

    # Check the object if we still have nothing
    if not description:
        obj = context.get('object', None)

        if obj:
            field = getattr(obj, 'description', None) or getattr(obj, 'summary', None)

            description = do_striptags(truncate_paragraphs(field, 1)) if field else None

    # If we are still None, look at page content
    if not description:
        # Get current page from request
        request = context['request']
        current_page = request.pages.current
        homepage = request.pages.homepage

        # Use either the current page twitter description, or the homepage twitter description
        if current_page:
            description = current_page.twitter_description

        if not description and homepage:
            description = homepage.twitter_description

        # If everything fails, fallback to OG tag title
        if not description:
            description = get_og_description(context)

    # Return description, or an empty string if nothing is working
    return escape(description or '')


@library.global_function
@jinja2.contextfunction
def get_twitter_image(context, image=None):
    '''
    Returns an appropriate Twitter image for the current page, falling back
    to the Open Graph image if it is set.
    '''
    image_obj = None

    # Load from context if exists
    if not image:
        image = context.get('twitter_image')

    # Check the object if we still have nothing
    if not image:
        obj = context.get('object')

        if obj:
            field = getattr(obj, 'image', None) or getattr(obj, 'photo', None) or getattr(obj, 'logo', None)

            image_obj = field if field else None

    # Get current page from request
    request = context['request']

    # If we are still None, look at page content
    if not image and not image_obj:
        current_page = request.pages.current
        homepage = request.pages.homepage

        # Use either the current page twitter image, or the homepage twitter image
        if current_page:
            image = current_page.twitter_image

        if not image and homepage:
            image = homepage.twitter_image

        # If everything fails, fallback to OG tag title
        if not image:
            return get_og_image(context)

    # If its a file object, load the URL manually
    if image_obj:
        return '{}{}'.format(
            absolute_domain_url(context),
            image_obj.get_absolute_url()
        )

    if image:
        return '{}{}'.format(
            absolute_domain_url(context),
            image.get_absolute_url()
        )

    # Return image, or an empty string if nothing is working
    return None


@library.global_function
@library.render_with('pages/title.html')
@jinja2.contextfunction
def render_title(context, browser_title=None):
    '''
    Renders the title of the current page::

        {% title %}

    You can override the title by setting a context variable called 'title'::

        {% with "foo" as title %}
            {% title %}
        {% endwith %}

    You can also provide the title as an argument to this tag::

        {% title "foo" %}

    '''
    request = context['request']
    page = request.pages.current
    homepage = request.pages.homepage
    # Render the title template.
    return {
        'title': browser_title or context.get('title') or (page and page.browser_title) or (page and page.title) or '',
        'site_title': (homepage and homepage.browser_title) or (homepage and homepage.title) or '',
        'site_name': settings.SITE_NAME or '',
    }


@library.global_function
@library.render_with('pages/breadcrumbs.html')
@jinja2.contextfunction
def render_breadcrumbs(context, page=None, extended=False):
    '''
    Renders the breadcrumbs trail for the current page::

        {% breadcrumbs %}

    To override and extend the breadcrumb trail within page applications, add
    the 'extended' flag to the tag and add your own breadcrumbs underneath::

        {% breadcrumbs extended=1 %}

    '''
    request = context['request']
    # Render the tag.
    page = page or request.pages.current
    if page:
        breadcrumb_list = [{
            'short_title': breadcrumb.short_title or breadcrumb.title,
            'title': breadcrumb.title,
            'url': breadcrumb.get_absolute_url(),
            'last': False,
            'page': breadcrumb,
        } for breadcrumb in request.pages.breadcrumbs]
    else:
        breadcrumb_list = []
    if not extended:
        breadcrumb_list[-1]['last'] = True
    # Render the breadcrumbs.
    return {
        'breadcrumbs': breadcrumb_list,
    }


@library.global_function
@jinja2.contextfunction
def get_country_code(context):
    if hasattr(context.request, 'country') and context.request.country:
        return '/{}'.format(
            context.request.country.code.lower()
        )

    return ''
