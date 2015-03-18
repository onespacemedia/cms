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
