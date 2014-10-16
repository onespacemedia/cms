"""
Production settings for {{ project_name }} project.

For an explanation of these settings, please see the Django documentation at:

<http://docs.djangoproject.com/en/dev/>

While many of these settings assume sensible defaults, you must provide values
for the site, database, media and email sections below.
"""

import os


# The name of this site.  Used for branding in the online admin area.

SITE_NAME = "Example"

SITE_DOMAIN = "example.com"

PREPEND_WWW = True

ALLOWED_HOSTS = [
    SITE_DOMAIN,
    'www.{}'.format(SITE_DOMAIN)
]

SUIT_CONFIG = {
    'ADMIN_NAME': SITE_NAME
}

# Database settings.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "{{ project_name }}",
        "USER": "{{ project_name }}",
        "PASSWORD": "",
        "HOST": "",
        "PORT": ""
    }
}


# Absolute path to the directory where all uploaded media files are stored.

MEDIA_ROOT = "/var/www/{{ project_name }}_media"

MEDIA_URL = "/media/"

FILE_UPLOAD_PERMISSIONS = 0o644


# Absolute path to the directory where static files will be collected.

STATIC_ROOT = "/var/www/{{ project_name }}_static"

STATIC_URL = "/static/"


# Email settings.

EMAIL_HOST = ""

EMAIL_HOST_USER = "{{ project_name }}"

EMAIL_HOST_PASSWORD = ""

EMAIL_PORT = 587

EMAIL_USE_TLS = True

SERVER_EMAIL = u"{name} <notifications@{domain}>".format(
    name=SITE_NAME,
    domain=SITE_DOMAIN,
)

DEFAULT_FROM_EMAIL = SERVER_EMAIL

EMAIL_SUBJECT_PREFIX = "[%s] " % SITE_NAME


# Error reporting settings.  Use these to set up automatic error notifications.

ADMINS = (
    ("Onespacemedia Errors", "errors@onespacemedia.com"),
)

MANAGERS = ()

SEND_BROKEN_LINK_EMAILS = False


# Locale settings.

TIME_ZONE = "Europe/London"

LANGUAGE_CODE = "en-gb"

USE_I18N = False

USE_L10N = True

USE_TZ = True


# Auto-discovery of project location.

SITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


# A list of additional installed applications.

INSTALLED_APPS = (
    "django.contrib.sessions",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "suit",
    "django.contrib.admin",
    "django.contrib.sitemaps",

    "optimizations",
    "reversion",
    "usertools",
    "historylinks",
    "watson",

    "cms",
    "cms.apps.pages",
    "cms.apps.links",
    "cms.apps.media",
    "cms.apps.news",

    "{{ project_name }}.apps.site",
    "{{ project_name }}.apps.faqs",
    "{{ project_name }}.apps.jobs",
    "{{ project_name }}.apps.people",

    'django_extensions',
)


# Additional static file locations.

STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, "static"),
)

STATIC_ASSETS = {
    "default": {
        "js": {
            "include": (
                "js/vendor/jquery.js",
                "js/foundation/foundation.js",
                "js/*.js",
            ),
            "exclude": (
                "js/jquery.cms.pages.js",
            ),
        },
        "css": {
            "include": (
                "css/screen.css",
            ),
        },
    },
}

# Dispatch settings.

MIDDLEWARE_CLASSES = (
    "django.middleware.transaction.TransactionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "watson.middleware.SearchContextMiddleware",
    "historylinks.middleware.HistoryLinkFallbackMiddleware",
    "cms.middleware.PublicationMiddleware",
    "cms.apps.pages.middleware.PageMiddleware",
)

ROOT_URLCONF = "{{ project_name }}.urls"

WSGI_APPLICATION = "{{ project_name }}.wsgi.application"

PUBLICATION_MIDDLEWARE_EXCLUDE_URLS = (
    "^admin/.*",
)

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

SITE_ID = 1


# Absolute path to the directory where templates are stored.

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, "templates"),
)

TEMPLATE_LOADERS = (
    ("django.template.loaders.cached.Loader", (
        "django.template.loaders.filesystem.Loader",
        "django.template.loaders.app_directories.Loader",
    )),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "cms.context_processors.settings",
    "cms.apps.pages.context_processors.pages",
)


# Namespace for cache keys, if using a process-shared cache.

CACHE_MIDDLEWARE_KEY_PREFIX = "{{ project_name }}"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    # Used for efficient caching of static assets.
    "optimizations": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 60 * 60 * 24,
        "LOCATION": "optimizations",
    },
}


# A secret key used for cryptographic algorithms.

SECRET_KEY = "{{ secret_key }}"


# TinyMCE settings.

RICHTEXT_SETTINGS = {
    "default": {
        "theme": "advanced",
        "plugins": "table, advimage, inlinepopups, paste",
        "paste_auto_cleanup_on_paste": True,
        "paste_remove_spans": True,
        "paste_remove_styles": True,
        "theme_advanced_buttons1": "code,|,formatselect,styleselect,|,bullist,numlist,table,hr,|,bold,italic,|,link,unlink,image",
        "theme_advanced_buttons2": "",
        "theme_advanced_buttons3": "",
        "theme_advanced_resizing": True,
        "theme_advanced_path": False,
        "theme_advanced_statusbar_location": "bottom",
        "width": "700px",
        "height": "350px",
        "dialog_type": "modal",
        "theme_advanced_blockformats": "h1,h2,h3,h4,h5,h6,p",
        "content_css": "css/screen.content.css",
        "extended_valid_elements": "iframe[scrolling|frameborder|class|id|src|width|height|name|align],article[id|class],section[id|class]",
        "convert_urls": False,
        "accessibility_warnings": False,
    }
}


NEWS_APPROVAL_SYSTEM = False
