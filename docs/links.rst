Links Module
============

The Links module provides a new page content type named "Link" which allows you to have a navigation item without a page associated.

Configuration
-------------

Ensure both ``cms.apps.pages`` and ``cms.apps.links`` are in your project's ``INSTALLED_APPS`` then add the new model to your database with the following::

    $ ./manage.py migrate

Usage
-----

To add a Link to your site simply add a Page. If you have more than one content type you will be shown a page such as this:

.. image :: img/content_types_link.png

If you do not have any other page content types you will be taken straight to the add form.  The form itself is very straightforward, simply add the Title for the page and a URL to redirect to.
