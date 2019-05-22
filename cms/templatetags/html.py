'''Template tags used for processing HTML.'''

from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django_jinja import library

from cms.html import process as process_html


@library.filter
@stringfilter
def html(text):
    '''
    Processes HTML text.

    The text is checked for permalinks embedded in <a> tags, expanding the
    permalinks to their referenced URL. Images containing a permalink source
    are checked for size and thumbnailed as appropriate.
    '''
    if not text:
        return ''
    text = process_html(text)
    return mark_safe(text)


@library.filter
@stringfilter
def truncate_paragraphs(text, number):
    '''Returns HTML text truncated to the given number of paragraphs.'''
    position = 0
    count = 0
    while count < number and position < len(text):
        position = text.find('</p>', position)
        if position == -1:
            position = len(text)
        else:
            position += 4
        count += 1
    return text[:position]
