'''Context processors used by the CMS.'''

from django.conf import settings as django_settings

from . import VERSION


def settings(request):
    '''Makes Django settings available in templates.'''
    context = {
        'settings': django_settings,
        'cms_version': VERSION,
    }
    return context
