onespacemedia-cms
=================

A collection of Django extensions that add content-management facilities to Django projects, forked from [etianen/cms](https://github.com/etianen/cms).


Overview
--------

The term *Content Management System* means different things to different people.
Rather than attempting to create a single monolithic solution to fit all needs, this project uses
a modular approach, allowing you to pick the parts you need, and extend it where necessary.

**Core features:**

*   Publication controls with online preview.
*   Pre-configured WYSIWYG editor widgets.
*   Hierarchal page management with no depth limit.
*   Image and file management, with easy embedding via WYSIWYG editors or pure model fields.

**Optional additional features:**

*   Version control and rollback (via [django-reversion](https://github.com/etianen/django-reversion)).
*   Automatic SEO-friendly redirect management (via [django-historylinks](https://github.com/etianen/django-historylinks)).
*   Full-text search with relevance ranking (via [django-watson](https://github.com/etianen/django-watson)).
*   Internal / external links in menus (via bundled [Links app](https://github.com/etianen/cms/wiki/links-app)).
*   Simple blog managment (via bundled [News app](https://github.com/etianen/cms/wiki/news-app)).
*   FAQs module
*   Jobs module
*   People module


Please note
-----------

This fork of etianen-cms contains many modifications which are specific to the needs of [Onespacemedia](http://onespacemedia.com). You may prefer to use the [original repository](https://github.com/etianen/cms) instead of this one.

Starting a new project
-------------

* Install the CMS with `pip install onespacemedia-cms`
* Run `start_cms_project.py testing .`, replacing `testing` with your project name.
* Answer a few questions regarding optional applications.
* Run `./manage.py migrate` then `./manage.py createsuperuser`.
