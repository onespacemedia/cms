Pages Module
============

The pages module is a standard CMS module which allows users to add pages to the website. However, it does not do anything by itself, it requires you to add models which extend `ContentBase  <https://github.com/onespacemedia/cms/blob/dd759528a57ccd917b65a3395c098c5d7622e9cb/cms/apps/pages/models.py#L379>`_.

How it works
------------

In ``cms.apps.pages.models`` there is a model named ``Page``, which contains a set of generic page fields such as ``parent``, ``publication_date``, ``expiry_date`` and so on.  To be able to add a ``Page`` to the site, we need a "Content Model".  A Content Model is a way of representing a type of page, this could be a homepage, a standard page, a contact page etc -- each Content Model would have it's own front-end template thus allowing you to provide different layout types, themes etc throughout your site.

The default CMS project contains an example Content Model in `site/models.py <https://github.com/onespacemedia/cms/blob/dd759528a57ccd917b65a3395c098c5d7622e9cb/cms/project_template/project_name/apps/site/models.py>`_ (but is commented out by default to avoid an initial migration being made by mistake).  Here's the same example::

    from django.db import models

    from cms.apps.pages.models import ContentBase


    class Content(ContentBase):

        content = models.TextField(
            blank=True,
        )

As you can see, this will create a Page type named 'Content' with a textarea named 'content'.  In addition to our custom field, we will have the following fields:

* Title
* URL Title (which will automatically populate as you type into the Title field)
* Parent page selector
* Publication date
* Expiry date
* Online status
* Navigation title (if you want a shorter version of the Page name to show in the navigation)
* "Add to navigation" selection, allowing you to add / remove the page from the navigation
* SEO controls:

  * Browser title
  * Page keywords
  * Page description
  * Sitemap priority
  * Sitemap change frequency
  * Allow index
  * Follow links
  * Allow archiving

If we wanted to have another page type with a different set of fields (or even the same fields) we simply have to add another model which extends ``ContentBase``, like so::

    from django.db import models

    from cms.apps.pages.models import ContentBase


    class Content(ContentBase):

        content = models.TextField(
            blank=True,
        )


    class ContentTwo(ContentBase):

        content = models.TextField(
            blank=True,
        )

With this structure in place, we would then get a choice of content types when adding a page.

.. image :: img/content_types.png

Context processor
-----------------

The pages module automatically adds a variable named ``pages`` to your template context, this gives you access to the page data and content for the current page and the homepage.  Let's assume your model looks like this::

    from django.db import models

    from cms.apps.pages.models import ContentBase


    class Content(ContentBase):

        introduction = models.TextField(
            blank=True,
        )

You can access the page data like this::

    <!-- The Page object -->
    {{ pages.current }}

    <!-- The Content model (which extends ContentBase) -->
    {{ pages.current.content }}

    <!-- Fields on the Page model -->
    {{ pages.current.title }}
    {{ pages.current.slug }}

    <!-- Fields on the Content model -->
    {{ pages.current.content.introduction }}

The ``content`` attribute on the ``Page`` model is a method which performs a ContentType lookup against the content ID allowing access to the fields of the Content model.

Template tags
-------------

A collection of template tags are included with the pages module, mostly for the purposes of simplifying SEO.  You can load them into the template like this::

    {% load pages %}

.. py:method:: navigation(context, pages, section=None)

Renders the site navigation using the template specified at ``pages/navigation.html``. By default this is just an unordered list with each navigation item as a list item.  The simplest usage is like this::

    {% navigation pages.homepage.navigation %}

Which would produce an output like this::

    <ul>
        <li>
            <a href="/page-1/">Page One</a>
        </li>

        <li>
            <a href="/page-2/">Page Two</a>
        </li>
    </ul>

If you would like the "base page" (the page that the navigation is being based off) to be included in the navigation simply add the ``section`` kwarg::

    {% navigation pages.homepage.navigation section=pages.homepage %}

The output of this would be::

    <ul>
        <li>
            <a class="here" href="/">Homepage</a>
        </li>

        <li>
            <a href="/page-1/">Page One</a>
        </li>

        <li>
            <a href="/page-2/">Page Two</a>
        </li>
    </ul>

.. py:method:: get_navigation(context, pages, section=None)

This is a wrapper around ``navigation``, but returns the navigation list instead of rendering it out to the page.

.. py:method:: page_url(page, view_func=None, *args, **kwargs)

Gets the URL of a Page's view function.

TODO: Expand on this.

.. py:method:: meta_description(context, description=None)

Renders the content of the meta description tag for the current page::

    {% meta_description %}

You can override the meta description by setting a context variable called ``meta_description``::

    {% with "foo" as meta_description %}
        {% meta_description %}
    {% endwith %}

You can also provide the meta description as an argument to this tag::

    {% meta_description "foo" %}

.. py:method:: meta_keywords(context, keywords=None)

Renders the content of the meta keywords tag for the current page::

    {% meta_keywords %}

You can override the meta keywords by setting a context variable called ``meta_keywords``::

    {% with "foo" as meta_keywords %}
        {% meta_keywords %}
    {% endwith %}

You can also provide the meta keywords as an argument to this tag::

    {% meta_keywords "foo" %}


.. py:method:: meta_robots(context, index=None, follow=None, archive=None)

Renders the content of the meta robots tag for the current page::

    {% meta_robots %}

You can override the meta robots by setting boolean context variables called
``robots_index``, ``robots_archive`` and ``robots_follow``::

    {% with 1 as robots_follow %}
        {% meta_robots %}
    {% endwith %}

You can also provide the meta robots as three boolean arguments to this
tag in the order 'index', 'follow' and 'archive'::

    {% meta_robots 1 1 1 %}

.. py:method:: title(context, browser_title=None)

Renders the title of the current page::

    {% title %}

You can override the title by setting a context variable called ``title``::

    {% with "foo" as title %}
        {% title %}
    {% endwith %}

You can also provide the title as an argument to this tag::

    {% title "foo" %}

.. py:method:: breadcrumbs(context, page=None, extended=False)

Renders the breadcrumbs trail for the current page::

    {% breadcrumbs %}

To override and extend the breadcrumb trail within page applications, add the ``extended`` flag to the tag and add your own breadcrumbs underneath::

    {% breadcrumbs extended=1 %}

.. py:method:: header(context, page_header=None)

Renders the header for the current page::

    {% header %}

You can override the page header by providing a ``header`` or ``title`` context variable. If both are present, then ``header`` overrides ``title``::

    {% with "foo" as header %}
        {% header %}
    {% endwith %}

You can also provide the header as an argument to this tag::

    {% header "foo" %}



FAQs
----

Can I change the content type after the page has been created?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, but it has risks.  Changing the content type will cause you to lose data in any fields which don't exist in the new model, that is to say that if your structure looks like this::


    class Content(ContentBase):

        content = models.TextField(
            blank=True,
        )


    class ContentTwo(ContentBase):

        content = models.TextField(
            blank=True,
        )

You can switch without issue as they have the same fields, however if your models look like this::

    class Content(ContentBase):

        content = models.TextField(
            blank=True,
        )


    class ContentTwo(ContentBase):

        description = models.TextField(
            blank=True,
        )

You would lose the data in the ``content`` field (on save) if you switched the content type from ``Content`` to ``ContentTwo``.

If you still want to change the content type, then it's reasonably simple.

#. Go to the create page of the content type you want to change *to*. Copy the number from the ``?type=XX`` portion of the URL.
#. Go to the edit page of the page you wish to switch.
#. Add ``?type=XX`` to the end of the URL.

At this point you will be looking at the fieldset for the new content type, but you will not have applied the changes.  If you're happy with the way your data looks hit Save and the changes will be saved.

Can I change the ModelAdmin ``fieldsets`` of a model admin view?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes. Simply add the ``fieldsets`` tuple to your model rather than your admin.py.

Can I set a ``filter_horizontal`` on a content model ManyToManyField?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes. Simply add the ``filter_horizontal`` tuple to your model rather than your admin.py.

Can I add inline model admins to content models?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes.  In your admin.py add code that looks like this::

    from django.contrib import admin

    from .models import Content, CarouselSlide

    from cms.apps.pages.admin import page_admin


    class CarouselSlideInline(admin.StackedInline):
        model = CarouselSlide

    page_admin.register_content_inline(Content, CarouselSlideInline)
