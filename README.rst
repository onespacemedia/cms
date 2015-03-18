onespacemedia-cms
=================

A collection of Django extensions that add content-management facilities
to Django projects, originally forked from
`etianen/cms <https://github.com/etianen/cms>`__. The team at
`Onespacemedia <http://www.onespacemedia.com>`__ are actively working on
the project, adding new features, updating existing ones and keeping it
working with the latest versions of Django.

The current version of ``onespacemedia-cms`` should always be compatible
with the current version of Django.

Notes
-----

A lot of the CMS has settings specific to how
`Onespacemedia <http://www.onespacemedia.com>`__ works and as such, you
will likely to need to change some of them to suit your needs. In
addition, this project installs a lot of other packages which you may
not need. You may prefer to use the `original
repository <https://github.com/etianen/cms>`__ instead of this one.

Features enabled by default
---------------------------

-  Publication controls with online preview.
-  Pre-configured WYSIWYG editor widgets (using
   `Redactor <http://imperavi.com/redactor/>`__)
-  Hierarchal page management with no depth limit.
-  Image and file management, with easy embedding via WYSIWYG editors or
   pure model fields.
-  Internal / external links in menus (via bundled [[Links app]].
-  Simple blog managment (via bundled [[News app]].
-  Version control and rollback (via
   `django-reversion <https://github.com/etianen/django-reversion>`__).
-  Automatic SEO-friendly redirect management (via
   `django-historylinks <https://github.com/etianen/django-historylinks>`__).
-  Full-text search with relevance ranking (via
   `django-watson <https://github.com/etianen/django-watson>`__).
-  Full ORM caching (via
   `django-cachalot <https://github.com/BertrandBordage/django-cachalot>`__).
-  CSS and JS compression (via
   `django-compressor <https://github.com/django-compressor/django-compressor>`__).
-  Image thumbnailing (via
   `sorl.thumbnail <https://github.com/mariocesar/sorl-thumbnail>`__).
-  Deployment and server management (via
   `server-management <https://github.com/onespacemedia/server-management>`__).

Optional Features
-----------------

-  FAQs module (via
   `cms-faqs <https://github.com/onespacemedia/cms-faqs/>`__)
-  Jobs module (via
   `cms-jobs <https://github.com/onespacemedia/cms-jobs/>`__)
-  People module (via
   `cms-people <https://github.com/onespacemedia/cms-people/>`__)
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

Installation
------------

To install ``onespacemedia-cms`` simply run:

::

    $ pip install onespacemedia-cms

If you want the ability to invite users via the admin, then run:

::

    $ pip install onespacemedia-cms[usertools]

Once the project has been installed, you can create a project with the
following command:

::

    $ start_cms_project.py project_name .

Where ``project_name`` is the name of your project and ``.`` is the
current directory (this will cause the ``manage.py`` to be created in
your working directory, rather than in a subfolder.

You should now run the following:

::

    $ ./manage.py migrate
    $ ./manage.py createsuperuser

Configuration
-------------

The ``start_cms_project.py`` takes care of a lot of the settings
automatically, but it's worth taking a look through the
``settings/base.py`` and updating any settings which still require
values, the key ones being:

-  ``SITE_NAME``
-  ``SITE_DOMAIN``
-  ``EMAIL_HOST`` / ``EMAIL_HOST_USER`` / ``EMAIL_HOST_PASSWORD``
-  ``ADMINS``
-  ``WHITELISTED_DOMAINS``

To configure the various third-party integrations, you will need to
generate API keys on each of the platforms and add them to the base
settings file.

 Google+ Authentication API
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Log in to the `Google Developers
   Console <https://console.developers.google.com/project>`__.
2. Click "Create Project".

   1. Enter your Project Name.
   2. (optional) Click "Show advanced options.." and change the data
      center location.
   3. Click "Create".

3. Click APIs & auth -> Consent screen.

   1. Select your Email Address.
   2. Enter your Product Name.
   3. Click "Save".

4. Click APIs & auth -> APIs

   1. Enable the "Google+ API".

5. Click APIs & auth -> Credentials

   1. Click "Create new Client ID"
   2. Enter your domain name into the "Authorized Javascript Origins"
      textarea.
   3. Click "Create Client ID".

6. Copy the "Client ID" to the setting named
   ``SOCIAL_AUTH_GOOGLE_PLUS_KEY``.
7. Copy the "Client Secret" to the setting named
   ``SOCIAL_AUTH_GOOGLE_PLUS_SECRET``.

 Adobe Creative SDK
~~~~~~~~~~~~~~~~~~~

1.  Log in to the `Adobe
    website <https://creativesdk.adobe.com/myapps.html>`__.
2.  Click "New Application".
3.  Enter your application name.
4.  Select "Web".
5.  Enter a description.
6.  Fill out the CAPTCHA.
7.  Click "Add Application".
8.  Copy the secret key to ``ADOBE_CREATIVE_SDK_CLIENT_SECRET``.
9.  Copy the API key to ``ADOBE_CREATIVE_SDK_CLIENT_ID``.
10. Set ``ADOBE_CREATIVE_SDK_CLIENT_ID`` to ``True``.

Sentry
~~~~~~

1. Log in to `Sentry <https://app.getsentry.com>`__
2. Create a new Project.
3. Enter the Name.
4. Set Platform to Django.
5. Click "Save Changes".
6. Copy the DSN from the modal window to the empty string in
   ``settings/production.py``.
