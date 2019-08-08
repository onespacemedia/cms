Onespacemedia CMS Documentation
===============================

Onespacemedia CMS is a collection of Django extensions that add content-management facilities to Django projects, originally forked from `etianen/cms <https://github.com/etianen/cms>`_. The team at `Onespacemedia <http://www.onespacemedia.com>`_ are actively working on the project, adding new features, updating existing ones and keeping it working with the latest versions of Django.

The current version of onespacemedia-cms should always be compatible with the current LTS version of Django.

Features enabled by default
---------------------------

-  Publication controls with online preview.
-  Pre-configured WYSIWYG editor widgets (using `TinyMCE <http://imperavi.com/redactor/>`_)
-  Hierarchal page management with no depth limit.
-  Image and file management, with easy embedding via WYSIWYG editors or pure model fields.
-  Internal / external links in menus (via bundled [[Links app]]).
-  Version control and rollback (via `django-reversion <https://github.com/etianen/django-reversion>`_).
-  Automatic SEO-friendly redirect management (via `django-historylinks <https://github.com/etianen/django-historylinks>`_).
-  Full-text search with relevance ranking (via `django-watson <https://github.com/etianen/django-watson>`_).

Optional Features
-----------------

-  Photoshop-like image editing.
-  Admin login via Google+.

.. toctree::
   :maxdepth: 1
   :glob:

   getting_started
   links
   media
   pages
   testing
   plugins/*
