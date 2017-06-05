import os
import platform
import random
import sys

import pytest
from django.conf import settings
from django.db import connection


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        cur = connection.cursor()
        cur.execute('ALTER SEQUENCE pages_page_id_seq RESTART WITH %s;', [random.randint(100, 200000)])


if platform.python_implementation() == 'PyPy':
    from psycopg2cffi import compat  # pylint: disable=import-error
    compat.register()


def pytest_configure():
    settings.configure(
        SITE_DOMAIN='example.com',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'py_{}'.format(sys.version_info[0]),
                'TEST': {
                    'NAME': 'py_{}'.format(sys.version_info[0]),
                }
            }
        },
        STATIC_URL='/static/',
        MEDIA_URL='/media/',
        INSTALLED_APPS=[
            # Django apps
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sitemaps',

            # CMS apps
            'cms.apps.links',
            'cms.apps.media',
            'cms.apps.pages',

            # Tests which contain custom models.
            'cms.tests',
            'cms.plugins.moderation.tests',

            # Third party apps
            'sorl.thumbnail',
            'historylinks',
            'reversion',
            'watson',
        ],
        ROOT_URLCONF='cms.tests.urls',
        ALLOWED_HOSTS=['*'],
        TEMPLATES=[
            {
                'BACKEND': 'django_jinja.backend.Jinja2',
                'DIRS': [
                    os.path.join('cms', 'templates'),
                    os.path.join('cms', 'tests', 'templates'),
                ],
                'APP_DIRS': True,
                'OPTIONS': {
                    'match_extension': '.html',
                    'match_regex': r'^(?!admin/|reversion/|registration/).*',
                    'app_dirname': 'templates',
                    'newstyle_gettext': True,
                    'bytecode_cache': {
                        'name': 'default',
                        'backend': 'django_jinja.cache.BytecodeCache',
                        'enabled': False,
                    },
                    'autoescape': True,
                    'auto_reload': False,
                    'translation_engine': 'django.utils.translation',
                    'context_processors': [
                        'django.contrib.auth.context_processors.auth',
                        'django.template.context_processors.debug',
                        'django.template.context_processors.i18n',
                        'django.template.context_processors.media',
                        'django.template.context_processors.static',
                        'django.contrib.messages.context_processors.messages',
                        'django.template.context_processors.request',
                        'cms.context_processors.settings',
                        'cms.apps.pages.context_processors.pages',
                    ]
                }
            },
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [
                    os.path.join('cms', 'tests', 'templates'),
                ],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.contrib.auth.context_processors.auth',
                        'django.template.context_processors.debug',
                        'django.template.context_processors.i18n',
                        'django.template.context_processors.media',
                        'django.template.context_processors.static',
                        'django.contrib.messages.context_processors.messages',
                        'django.template.context_processors.request',
                        'cms.context_processors.settings',
                        'cms.apps.pages.context_processors.pages',
                    ]
                }
            }
        ],
        GEOIP_PATH=os.path.join('cms', 'tests', 'geoip'),
    )
