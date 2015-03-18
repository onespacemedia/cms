Getting Started
===============

Installation
------------

To install onespacemedia-cms simply run::

   $ pip install onespacemedia-cms

If you want the ability to invite users via the admin, then run::

   $ pip install onespacemedia-cms[usertools]

Once the project has been installed, you can create a project with the following command::

   $ start_cms_project.py project_name .

Where ``project_name`` is the name of your project and ``.`` is the current directory (this will cause the ``manage.py`` to be created in your working directory, rather than in a subfolder.

You should now run the following::

   $ ./manage.py migrate
   $ ./manage.py createsuperuser

Configuration
-------------

``start_cms_project.py`` takes care of a lot of the settings automatically, but it's worth taking a look through the ``settings/base.py`` and updating any settings which still require values, the key ones being:

-  ``SITE_NAME``
-  ``SITE_DOMAIN``
-  ``EMAIL_HOST`` / ``EMAIL_HOST_USER`` / ``EMAIL_HOST_PASSWORD``
-  ``ADMINS``
-  ``WHITELISTED_DOMAINS``

To configure the various third-party integrations, you will need to generate API keys on each of the platforms and add them to the base settings file.

Google+ Authentication API
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Log in to the `Google Developers Console <https://console.developers.google.com/project>`__.
2. Click "Create Project".

   1. Enter your Project Name.
   2. (optional) Click "Show advanced options.." and change the data center location.
   3. Click "Create".

3. Click APIs & auth -> Consent screen.

   1. Select your Email Address.
   2. Enter your Product Name.
   3. Click "Save".

4. Click APIs & auth -> APIs

   1. Enable the "Google+ API".

5. Click APIs & auth -> Credentials

   1. Click "Create new Client ID"
   2. Enter your domain name into the "Authorized Javascript Origins" textarea.
   3. Click "Create Client ID".

6. Copy the "Client ID" to the setting named ``SOCIAL_AUTH_GOOGLE_PLUS_KEY``.
7. Copy the "Client Secret" to the setting named ``SOCIAL_AUTH_GOOGLE_PLUS_SECRET``.

Adobe Creative SDK
~~~~~~~~~~~~~~~~~~

1.  Log in to the `Adobe website <https://creativesdk.adobe.com/myapps.html>`_.
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
6. Copy the DSN from the modal window to the empty string in ``settings/production.py``.
