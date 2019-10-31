# Onespacemedia CMS documentation

Onespacemedia CMS is a collection of Django extensions that add content-management facilities to Django projects, originally forked from [etianen/cms](https://github.com/etianen/cms).
The team at [Onespacemedia](http://www.onespacemedia.com>) are actively working on the project, adding new features, updating existing ones and keeping it working with the latest versions of Django.

## Requirements

Onespacemedia CMS assumes Jinja2 templating with [django-jinja](https://github.com/niwinz/django-jinja), and very little else.

## Features

onespacemedia-cms comes with a minimal feature set by default.
It has no opinions about how your project should be structured, it has minimal opinions about how the admin looks, and it plays well with your existing models.

-  Hierarchal [page management](pages-app.md) with no depth limit.
-  [Publication controls](publication-control.md) with online preview.
-  Pre-configured WYSIWYG editor widgets (using TinyMCE).
-  [Image and file management](media-app.md), with easy embedding via WYSIWYG editors or pure model fields.
-  Internal / external links in menus (via bundled optional [links app](links-app.md)).
-  Version control and rollback (via [django-reversion](https://github.com/etianen/django-reversion)).
-  Automatic SEO-friendly redirect management (via [django-historylinks](https://github.com/etianen/django-historylinks)).
-  Full-text search with relevance ranking (via [django-watson](https://github.com/etianen/django-watson)).
-  Many [helper models](helpers.md) and views for SEO-friendly user-visible models.

## Getting started

* Read the [walkthrough](walkthrough.md).
* Clone and have a poke around the [accompanying tiny CMS project repo](https://github.com/onespacemedia/tiny-cms-project).
* For a full-fledged CMS project with some skeletal apps, see our [project template](https://github.com/onespacemedia/project-template).

## Editing this document

This is a [docsify](https://docsify.js.org/) document. For an optimal editing experience:

```
npm install -g docsify-cli
docsify serve docs/
```
