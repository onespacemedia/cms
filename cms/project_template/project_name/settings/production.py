from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

# Sentry config.
RAVEN_CONFIG = {
    'dsn': '',
}
