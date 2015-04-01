Onespacemedia CMS Documentation
===============================

A collection of Django extensions that add content-management facilities to Django projects, originally forked from `etianen/cms <https://github.com/etianen/cms>`_. The team at `Onespacemedia <http://www.onespacemedia.com>`_ are actively working on the project, adding new features, updating existing ones and keeping it working with the latest versions of Django.

The current version of onespacemedia-cms should always be compatible with the current version of Django.

.. note:: A lot of the CMS has settings specific to how `Onespacemedia <http://www.onespacemedia.com>`_ works and as such you will likely to need to change some of them to suit your needs. In addition, this project installs a lot of other packages which you may not need. You may prefer to use the `original repository <https://github.com/etianen/cms>`_ instead of this one.

Features enabled by default
---------------------------

-  Publication controls with online preview.
-  Pre-configured WYSIWYG editor widgets (using `Redactor <http://imperavi.com/redactor/>`_)
-  Hierarchal page management with no depth limit.
-  Image and file management, with easy embedding via WYSIWYG editors or pure model fields.
-  Internal / external links in menus (via bundled [[Links app]].
-  Simple blog managment (via bundled [[News app]].
-  Version control and rollback (via `django-reversion <https://github.com/etianen/django-reversion>`_).
-  Automatic SEO-friendly redirect management (via `django-historylinks <https://github.com/etianen/django-historylinks>`_).
-  Full-text search with relevance ranking (via `django-watson <https://github.com/etianen/django-watson>`_).
-  Full ORM caching (via `django-cachalot <https://github.com/BertrandBordage/django-cachalot>`_).
-  CSS and JS compression (via `django-compressor <https://github.com/django-compressor/django-compressor>`_).
-  Image thumbnailing (via `sorl.thumbnail <https://github.com/mariocesar/sorl-thumbnail>`_).
-  Deployment and server management (via `server-management <https://github.com/onespacemedia/server-management>`_).

Optional Features
-----------------

-  FAQs module (via `cms-faqs <https://github.com/onespacemedia/cms-faqs/>`_)
-  Jobs module (via `cms-jobs <https://github.com/onespacemedia/cms-jobs/>`_)
-  People module (via `cms-people <https://github.com/onespacemedia/cms-people/>`_)
-  Photoshop-like image editing.
-  Admin login via Google+.
-  News approval system.

Integrations
------------

The CMS integrates directly with a lot of third-party services, and it's
usually worth configuring them to get even greater benefit from the CMS.
Currently supported are:

-  Adobe Creative SDK (formerly known as Aviary).
-  Sentry.
-  Google+ authentication API.

.. toctree::
   :maxdepth: 1

   getting_started
   links
   media
   news
   pages
   testing
