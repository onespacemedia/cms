from django import template

register = template.Library()


@register.filter
def here(page, request):
    return request.path.startswith(page.get_absolute_url())
