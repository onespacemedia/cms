"""Permalink generation template tags."""
import jinja2

from django.utils.html import escape

from cms import permalinks
from django_jinja import library


@library.filter
def permalink(model):
    """Returns a permalink for the given model."""
    return permalinks.create(model)


@library.global_function
@jinja2.contextfunction
def get_permalink_absolute(context, model):
    request = context["request"]

    return escape(request.build_absolute_uri(permalinks.create(model)))
