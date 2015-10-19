from django import template

register = template.Library()


@register.filter
def here(page, request):
    return request.path.startswith(page.get_absolute_url())


@register.simple_tag
def node_module(path):
    """
    Used like the Django {% static %} template tag, but uses the node_modules,
    directory instead
    :param path:
    :return:
    """
    return '/node_modules/{}'.format(path)
