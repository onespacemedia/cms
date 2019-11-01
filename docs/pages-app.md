# The Pages app

`cms.apps.pages` allows users to add a page tree and page content to the website. However, it does not do anything by itself; It requires you to add models into your project which inherit from `cms.apps.pages.models.ContentBase`.

## How it works

In `cms.apps.pages.models` there is a model named `Page`, which contains a set of generic page fields such as `parent`, `publication_date`, `expiry_date` and so on.

To be able to add a `Page` to the site, we need a content model.  A content model is a way of representing a type of page. This could be a homepage, a standard page, a contact page etc -- each content model would have its own front-end template thus allowing you to provide different layout types, themes etc throughout your site.

Here is an example of a content model::


```python
from cms.apps.pages.models import ContentBase
from django.db import models


class Content(ContentBase):

    content = models.TextField(
        blank=True,
    )
```


As you can see, this will create a page content type named 'Content' with a textarea named 'content'.  In addition to our custom field, we will have the following fields:

* Title
* Slug (automatically populated as you type into the Title field)
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

None of these exist on your content model; they are on the page to which a content model instance is attached. The fields from your content model are dynamically injected into the editing form in your admin. If you'd like to see the hairy details of how this works, see `get_form` in `apps/pages/admin.py`.

If we wanted to have another page type with a different set of fields (or even the same fields) we simply have to add another model which extends `ContentBase`, like so::

```
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
```

With this structure in place, we would then get a choice of content types when adding a new page.

## Context processor

The pages module automatically adds a variable named `pages` to your template context. This gives you access to the page data and content for the current page and the homepage.  Let's assume your model looks like this:


```
from cms.apps.pages.models import ContentBase
from django.db import models


class Content(ContentBase):

    introduction = models.TextField(
        blank=True,
    )
```

You can access the page data in your template like this:

```
<!-- The currently active Page object -->
{{ pages.current }}

<!-- The Content model (which extends ContentBase) -->
{{ pages.current.content }}

<!-- Fields on the Page model -->
{{ pages.current.title }}
{{ pages.current.slug }}
```

The `content` attribute on the `Page` model is a cached property which performs a ContentType lookup against the content ID allowing access to the fields of the Content model:

```
<!-- Fields on the Content model -->
{{ pages.current.content.introduction }}
```

### How do I....

#### ...change the content type after the page has been created?

This has risks.  Changing the content type will cause you to lose data in any fields which don't exist in the new model. For example, if your models look like this:

```
class Content(ContentBase):

    content = models.TextField(
        blank=True,
    )


class ContentTwo(ContentBase):

    content = models.TextField(
        blank=True,
    )
```

You can switch without issue as they have the same fields. However, if your models look like this:

```
class Content(ContentBase):

    content = models.TextField(
        blank=True,
    )


class ContentTwo(ContentBase):

    description = models.TextField(
        blank=True,
    )
```

You would lose the data in the ``content`` field (on save) if you switched the content type from ``Content`` to ``ContentTwo``.

Any objects that have a `ForeignKey` with `on_delete=models.CASCADE` to your content model will also be deleted.

If you still want to change the content type, then it's reasonably simple.

1. Go to the create page of the content type you want to change *to*. Copy the number from the ``?type=XX`` portion of the URL.
2. Go to the edit page of the page you wish to switch.
3. Add ``?type=XX`` to the end of the URL.

At this point you will be looking at the fieldset for the new content type, but you will not have applied the changes.  If you're happy with the way your data looks hit Save and the changes will be saved.

#### ...change the ModelAdmin ``fieldsets`` of my content model?

Simply add the `fieldsets` tuple to your model rather than your admin.py.

#### ...set a `filter_horizontal` on a content model ManyToManyField?

Simply add the ``filter_horizontal`` tuple to your model rather than your admin.py.

#### ...add inline model admins to content models?

First, you need to add a ForeignKey from your inline model to `pages.Page` (note: *not* your content model!).

In your admin.py add code that looks like this:

```
from cms.apps.pages.admin import page_admin
from django.contrib import admin

from .models import ContentModel, CarouselSlide


class CarouselSlideInline(admin.StackedInline):
    model = CarouselSlide


page_admin.register_content_inline(ContentModel, CarouselSlideInline)
```
