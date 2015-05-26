from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
    'opbeat.contrib.django',
)

OPBEAT = {
    "ORGANIZATION_ID": "dde034beb33d4b77bb9937c39f0c158f",
    "APP_ID": "",
    "SECRET_TOKEN": ""
}

MIDDLEWARE_CLASSES = (
    'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
) + MIDDLEWARE_CLASSES
