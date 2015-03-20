News Module
===========

The News module is a standard news aggregation system which works in two parts.  The first part is a "News feed" which is a page content type designated as a container for articles.  You can have multiple news feeds in a site and assign articles to any one of them.

Features
--------

* Multiple news feeds per-site.
* Built-in RSS feeds.
* Archive views allowing you to see lists by year, month and date.
* Ability to add articles to categories.
* Ability to associate multiple authors with an article.
* An optional approval system.

The fields available on an Article are:

* Title
* News feed
* Date
* Status (if enabled)
* Image
* Content
* Summary
* Categories
* Authors
* Online / offline toggle


Configuration
-------------

Add ``cms.apps.news`` to your ``INSTALLED_APPS`` and then add the models to your database with::

    $ ./manage.py migrate

If you would like to enable the approval system set the following setting::

    NEWS_APPROVAL_SYSTEM = True


Usage
-----

First create a News Feed by adding a new page and selecting the "News feed" option then add an Article and select the newly created News feed.

If you have enabled the approval system an additional field appears on the edit form named ``status``.  By default the status is set to 'draft', users without the ``news.can_approve_articles`` permission can only set the status to either 'draft' or 'submitted'.  An article in either of these states will not appear on the front-end website, but is visible within the administration system.  Users with the appropriate permission are able to set articles to 'approved' and thus make the articles appear on the website.

Known issues
------------

* You cannot add fields to News Feeds or Articles easily, you have to copy the application into your project.

