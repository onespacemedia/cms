'''Permalink generation template tags.'''
import jinja2
from django.utils.html import escape
from django_jinja import library

from cms import permalinks


@library.filter
def permalink(obj):
    '''Returns a permalink for the given object.'''
    return permalinks.create(obj)


@library.global_function
@jinja2.contextfunction
def get_permalink_absolute(context, model):
    request = context['request']

    return escape(request.build_absolute_uri(permalinks.create(model)))
