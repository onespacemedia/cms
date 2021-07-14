'''Fields used by the page management application.'''

from urllib import parse as urlparse

from django.core.exceptions import ValidationError
from django.db import models


class HtmlField(models.TextField):

    '''A field that contains HTML data.'''

    def formfield(self, **kwargs):
        '''Returns a HtmlWidget.'''
        from cms.forms import HtmlWidget

        kwargs['widget'] = HtmlWidget
        return super().formfield(**kwargs)

    def get_internal_type(self):
        return 'HtmlField'


class LinkResolutionError(Exception):

    '''A link could not be resolved.'''


def resolve_link(value):
    '''Resolves the given link to a full URL.'''
    # Parse the URL.
    try:
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(value)
    except ValueError:
        pass
    else:
        # Check that it's not a relative URL.
        if not netloc and not scheme:
            if path.startswith('/'):
                # This is a local absolute URL.
                return value
            elif path.startswith('www.'):
                # This link was given without a scheme.
                scheme = 'http'
                path_parts = path.split('/', 1)
                netloc = path_parts[0]
                path = '/'
                if len(path_parts) == 2:
                    path = '/' + path_parts[1]
                # Recompose the URL.
                return urlparse.urlunparse((scheme, netloc, path, params, query, fragment,))
        if netloc and scheme:
            return value
    # Raise a validation error.
    raise LinkResolutionError('The link {!r} could not be resolved.'.format(value))


def link_validator(value):
    '''Validates the given link.'''
    try:
        resolve_link(value)
    except LinkResolutionError:
        raise ValidationError('Enter a valid URL.')


class LinkField(models.CharField):

    '''A field that contains an internal or external link.'''

    def __init__(self, *args, **kwargs):
        '''Initializes the LinkField.'''
        kwargs.setdefault('max_length', 1000)
        super().__init__(*args, **kwargs)
        self.validators.append(link_validator)

    def contribute_to_class(self, cls, name):
        '''Adds in an accessor for the resolved link.'''
        super().contribute_to_class(cls, name)

        def get_XXX_resolved(self):
            link = getattr(self, name, '')
            if link:
                try:
                    link = resolve_link(link)
                except LinkResolutionError:
                    pass
            return link
        setattr(cls, 'get_{}_resolved'.format(name), get_XXX_resolved)
