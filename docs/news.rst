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

Overriding templates
--------------------

The news app has a very granular set of templates, allowing you to change any aspect of the default output with very little effort.


Template hierarchy
^^^^^^^^^^^^^^^^^^

news/base.html
""""""""""""""

**Extends:** ``base.html``

**Includes:**

* news/includes/article_category_list.html
* news/includes/article_date_list.html


news/article_archive.html
"""""""""""""""""""""""""

**Extends:** ``news/base.html``

**Includes:**

* news/includes/archive_list.html
* news/includes/archive_list_item.html
* news/includes/article_meta.html

    * news/includes/article_date.html
    * news/includes/article_category_list.html


news/article_archive_day.html
"""""""""""""""""""""""""""""

**Extends:** ``news/article_archive.html``


news/article_archive_month.html
"""""""""""""""""""""""""""""""

**Extends:** ``news/article_archive.html``


news/article_archive_year.html
""""""""""""""""""""""""""""""

**Extends:** ``news/article_archive.html``

news/article_category_archive.html
""""""""""""""""""""""""""""""""""

**Extends:** ``news/base.html``

**Includes:**

* news/includes/article_list.html
* news/includes/article_list_item.html
* news/includes/article_meta.html

    * news/includes/article_date.html
    * news/includes/article_category_list.html


news/article_detail.html
""""""""""""""""""""""""

**Extends:** ``news/base.html``

**Includes:**

* news/includes/article_meta.html

    * news/includes/article_date.html
    * news/includes/article_category_list.html

Template tags
-------------

.. py:method:: article_list(context, article_list)

Renders a list of news articles.

.. py:method:: article_url(context, article, page)

Renders the URL for an article.

.. py:method:: article_list_item(context, article, page)

Renders an item in an article list.

.. py:method:: article_archive_url(context, page)

Renders the URL for the current article archive.

.. py:method:: category_url(context, category, page)

Renders the URL for the given category.

.. py:method:: category_list(context, category_list)

Renders a list of categories.

.. py:method:: article_year_archive_url(context, year, page)

Renders the year archive URL for the given year.

.. py:method:: article_day_archive_url(context, date, page)

Renders the month archive URL for the given date.

.. py:method:: article_date(context, article)

Renders a rich date for the given article.

.. py:method:: article_category_list(context, article)

Renders the list of article categories.

.. py:method:: article_meta(context, article)

Renders the metadata of an article.

.. py:method:: article_date_list(context, page)

Renders a list of dates.

.. py:method:: article_latest_list(context, page, limit=5)

Renders a widget-style list of latest articles.

.. py:method:: get_article_latest_list(context, page, limit=5)

A wrapper around ``article_latest_list`` which returns the dictionary rather than render it.

Known issues
------------

* You cannot add fields to News Feeds or Articles easily, you have to copy the application into your project.

