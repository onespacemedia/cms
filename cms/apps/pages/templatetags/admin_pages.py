from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def can_add_versions(context):
    obj = context.get('original')
    return obj and hasattr(obj, 'version_for') and 'cms.middleware.VersionMiddleware' in settings.MIDDLEWARE
