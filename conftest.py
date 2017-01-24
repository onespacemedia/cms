import os
import random
import sys

import pytest
from django.conf import settings
from django.db import connection


# The CMS tests use test-only models, which won't be loaded if we only load
# our real migration files, so point to a nonexistent one, which will make
# the test runner fall back to 'syncdb' behavior.

# Note: This will not catch a situation where a developer commits model
# changes without the migration files.

class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return 'notmigrations'


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        cur = connection.cursor()
        cur.execute('ALTER SEQUENCE pages_page_id_seq RESTART WITH %s;', [random.randint(10000, 20000)])


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
        MIGRATION_MODULES=DisableMigrations(),
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

            # Third party apps
            'sorl.thumbnail',
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
                        'django.core.context_processors.debug',
                        'django.core.context_processors.i18n',
                        'django.core.context_processors.media',
                        'django.core.context_processors.static',
                        'django.contrib.messages.context_processors.messages',
                        'django.core.context_processors.request',
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
                        'django.core.context_processors.debug',
                        'django.core.context_processors.i18n',
                        'django.core.context_processors.media',
                        'django.core.context_processors.static',
                        'django.contrib.messages.context_processors.messages',
                        'django.core.context_processors.request',
                        'cms.context_processors.settings',
                        'cms.apps.pages.context_processors.pages',
                    ]
                }
            }
        ],
        GEOIP_PATH=os.path.join('cms', 'tests', 'geoip'),
    )
