# The Pages app

## How it works

In `cms.apps.pages.models` there is a model named `Page`.
For now, we only want to think about three of its attributes: its title, its slug, and its parent.
These define the page's place in the page hierarchy.
From there, a tree of pages can be constructed.

### PageMiddleware

`cms.apps.pages.middleware.PageMiddleware` serves two important tasks.

First, it adds a `pages` attribute in its `process_request`. This is an instance of `cms.apps.pages.middleware.RequestPageManager`, which is a wrapper around the site's Page tree.
This gives you access to the page tree (as `request.pages`) any time you have access to the current request.

`RequestPageManager` has the following attributes, which are all cached properties:

* `current`: the currently-active Page object. This is the most interesting one, and the most commonly-accessed.
* `homepage`: the Page that has no parent, i.e. the home page of the site.
* `breadcrumbs`: A list representing a trail of pages from the current page to the homepage. For example, if a page called "Dreamies" had a parent of "Cat treats" whose parent was the home page, then the breadcrumb trail would take the form `[<Page: Home>, <Page: Cat treats>, <Page: Dreamies>]`.
* `section`: The closest element to the homepage in the tree. In our example above, this would be "Cat treats". If `current` is "Cat treats", it would be "Cat treats" again. If `current` is the homepage, it would be `None`.
* `subsection`: The closest page below `section`. It would be "Dreamies" in our example.

Secondly, it handles rendering the page at the current URL in its `process_response`.
If the current URL would otherwise be a 404, it attempts to find a page at the current URL.
For example, our "Dreamies" page probably lives at `/cat-treats/dreamies/`.

### Content models

The Page model mostly defines its title, its place in the page tree, and some hidden metadata fields.
It does not define any user-visible content; it is entirely agnostic about what content looks like.
It delegates this to **content models**.

A content model is a way of representing a type of page.
This could be a homepage, a standard page, a contact page, etc; this allows multiple layout types, themes etc throughout your site.

Here is an example of a content model:

```python
from cms.apps.pages.models import ContentBase
from django.db import models


class PlainPage(ContentBase):

    text = models.TextField(
        blank=True,
    )
```

As mentioned in the [walkthrough](walkthrough.md), any non-abstract derivative of `ContentBase` will be available as a page type in our admin.
No explicit registration is necessary.
Once you have created the model above, your "Add page" will have the "Plain page" content type available.

In addition to our "Text" field from our content model, we will have the following fields in the admin:

* Title
* Slug (automatically populated as you type into the Title field)
* Parent page selector
* Publication date
* Expiry date
* Online status
* Navigation title (if you want a shorter version of the Page name to show in the navigation)
* "Add to navigation" selection, allowing you to add / remove the page from the navigation
* OpenGraph (Facebook and others) card controls
* Twitter card controls
* SEO controls:
  * Browser title
  * Page keywords
  * Page description
  * Sitemap priority
  * Sitemap change frequency
  * Allow index
  * Follow links
  * Allow archiving

None of these exist on your content model; in fact, `ContentBase` has no user-visible fields at all.
They are on a Page object to which a content model instance is attached.
The fields from your content model are dynamically injected into the editing form in your admin.
If you'd like to see the hairy details of how this works, see `get_form` in `apps/pages/admin.py`.

If we wanted to have another page type with a different set of fields (or even the same fields) we simply have to add another model which extends `ContentBase`, like so:

```python
from django.db import models

from cms.apps.pages.models import ContentBase


class PlainPage(ContentBase):

    text = models.TextField(
        blank=True,
    )


class PlainPageTwo(ContentBase):

    text = models.TextField(
        blank=True,
    )
```

You can access the content object for a `Page` object via the its `content` attribute (actually a cached property).

### Rendering the current page

The middleware will attempt to render the page based on the content model's `urlconf` attribute.
This is a string containing a dotted path to a standard Django urlconf, and that urlconf will define how the current URL and paths below it will be rendered.
In our [walkthrough](walkthrough.md) we used this to create a news article list and a route for a news detail page, like this:

```python
urlconf = 'tiny_project.apps.news.urls'
```

You don't have to specify your own `urlconf` in your content model if you don't want to.
`ContentBase` has a default `urlconf` (`'cms.apps.pages.urls'`) that routes to a simple `TemplateView`.
That attempts to render a template living at `<app-label>`/`modelname.html`.
Thus, our default template for rendering our content model `PlainPage`, if it was in an app called `things`, would live at `things/plainpage.html`.

### The context processor

The pages module adds a key named `pages` to your template context.
This gives you access to the page data and content for the current page, as well as the rest of the pages tree.

Assuming the page's current content object is an instance of `PlainPage` above, you can access the page data in your template like this:

```
<!-- The currently active Page object -->
{{ pages.current }}

<!-- Fields on the Page model -->
{{ pages.current.title }}
{{ pages.current.slug }}

<!-- The content object (PlainPage instance) -->
{{ pages.current.content }}

<!-- `text` field on the content object -->
{{ pages.current.content.text }}
```

## How do I....

### ...change the content type after the page has been created?

This has risks. Changing the content type will cause you to lose data in any fields which don't exist in the new model. For example, if your models look like this:

```python
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

```python
class Content(ContentBase):

    content = models.TextField(
        blank=True,
    )


class ContentTwo(ContentBase):

    description = models.TextField(
        blank=True,
    )
```

You would lose the data in the `content` field (on save) if you switched the content type from `Content` to `ContentTwo`.

Any objects that have a `ForeignKey` with `on_delete=models.CASCADE` to your content model will also be deleted.

If you still want to change the content type, then it's reasonably simple.

1. Go to the create page of the content type you want to change *to*. Copy the number from the `?type=XX` portion of the URL.
2. Go to the edit page of the page you wish to switch.
3. Add `?type=XX` to the end of the URL.

At this point you will be looking at the fieldset for the new content type, but you will not have applied the changes.
If you're happy with the way your data looks hit Save.

### ...change the ModelAdmin `fieldsets` of my content model?

Add the `fieldsets` tuple to your model rather than your admin.py.

### ...set a `filter_horizontal` on a content model ManyToManyField?

Add the `filter_horizontal` tuple to your model rather than your admin.py.

### ...add inline model admins to content models?

First, you need to add a ForeignKey from your inline model to `pages.Page` (note: *not* your content model!).

In your admin.py add code that looks like this:

```python
from cms.apps.pages.admin import page_admin
from django.contrib import admin

from .models import ContentModel, CarouselSlide


class CarouselSlideInline(admin.StackedInline):
    model = CarouselSlide


page_admin.register_content_inline(ContentModel, CarouselSlideInline)
```
