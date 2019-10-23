# Onespacemedia CMS documentation

Onespacemedia CMS is a collection of Django extensions that add content-management facilities to Django projects, originally forked from [etianen/cms](https://github.com/etianen/cms). The team at [Onespacemedia](http://www.onespacemedia.com>) are actively working on the project, adding new features, updating existing ones and keeping it working with the latest versions of Django.

The current version of onespacemedia-cms should always be compatible with the current LTS version of Django.

## Requirements

Onespacemedia CMS assumes Jinja2 templating with [django-jinja](https://github.com/niwinz/django-jinja), search with [django-watson](https://github.com/etianen/django-watson/issues), and very little else.

## Features

onespacemedia-cms comes with very few features by default. It has no opinions about how your project should work, it has minimal opinions about how the admin looks, and it plays well with your existing models.

-  Hierarchal page management with no depth limit.
-  Publication controls with online preview.
-  Pre-configured WYSIWYG editor widgets (using TinyMCE)
-  Image and file management, with easy embedding via WYSIWYG editors or pure model fields.
-  Internal / external links in menus (via bundled `links` app).
-  Version control and rollback (via [django-reversion](https://github.com/etianen/django-reversion)).
-  Automatic SEO-friendly redirect management (via [django-historylinks](https://github.com/etianen/django-historylinks)).
-  Full-text search with relevance ranking (via [django-watson](https://github.com/etianen/django-watson)).
-  Many helper model classes and views for SEO-friendly user-visible models.

## Getting started

### Project template

Onespacemedia's [project template](https://github.com/onespacemedia/project-template) is the fastest way to get a new project started with onespacemedia-cms. It includes a set of basic apps, many useful helper functions & classes, and a front-end build system based on Node, Webpack and PostCSS. See the instructions in the [GitHub repository](https://github.com/onespacemedia/project-template>) for details.

### Installation on an existing project

To install `onespacemedia-cms` simply run:

```
$ pip install onespacemedia-cms
```

Add the CMS to your `INSTALLED_APPS`:

```
INSTALLED_APPS = [
    ...
    'cms',
    'cms.apps.pages',
    'cms.apps.media',
    'cms.apps.links',
]
```

Add the page middleware:

```
MIDDLEWARE = [
    ...
    'cms.middleware.PublicationMiddleware',
    'cms.apps.pages.middleware.PageMiddleware',
]
```

Finally, add `cms.apps.pages.context_processors.pages` to your template engine's `context_processors`.


You should now run the following:

```
$ ./manage.py migrate
```
