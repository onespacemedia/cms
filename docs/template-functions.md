# Jinja2 template functions

A collection of template functions are included with the pages module, mostly for the purposes of simplifying SEO.

## TL;DR

The `<head>` of your document should look like this:

```jinja2
<meta name="description" content="{{ get_meta_description() }}">
<meta name="robots" content="{{ get_meta_robots() }}">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5">
<!-- Open Graph data -->
<meta property="og:title" content="{{ get_og_title() }}">
<meta property="og:url" content="{{ get_canonical_url() }}">
<meta property="og:type" content="website">
<meta property="og:description" content="{{ get_og_description() }}">
<meta property="og:image" content="{{ get_og_image() }}">

<!-- Twitter card data -->
<meta name="twitter:card" content="{{ get_twitter_card() }}" />
<meta name="twitter:site" content="" />
<meta name="twitter:title" content="{{ get_twitter_title() }}" />
<meta name="twitter:description" content="{{ get_twitter_description() }}" />
<meta name="twitter:image" content="{{ get_twitter_image() }}" />

<title>{% block title %}{{ render_title() }}{% endblock %}</title>
```

## `render_navigation(pages, section=None)`

Renders the site navigation using the template specified at ``pages/navigation.html``. By default this is just an unordered list with each navigation item as a list item.  The simplest usage is like this::

    {{ render_navigation(pages.homepage.navigation) }}

Which would produce an output like this:

```
<ul>
    <li>
        <a href="/page-1/">Page One</a>
    </li>

    <li>
        <a href="/page-2/">Page Two</a>
    </li>
</ul>
```

If you would like the "base page" (the page that the navigation is being based off) to be included in the navigation simply add the ``section`` kwarg::

```
{{ render_navigation(pages.homepage.navigation, section=pages.homepage) }}
```

The output of this would be:

```
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
```

You will probably want to override the output in your project. For example, you'll almost certainly want to add class names, and to handle children of children. We suggest you make a local copy of `apps/pages/templates/pages/navigation.html` in your project.

## `get_navigation(pages, section=None)`

This is a wrapper around `navigation`, but returns the navigation list instead of rendering it out to the page.

## `get_page_url(page, view_func=None, *args, **kwargs)`

Gets the URL of a Page's view function.

TODO: Expand on this.

## `meta_description(description=None)`

Renders the content of the meta description tag for the current page::

```
<meta name="description" value="{{ get_meta_description() }}">
```

You can override the meta description by setting a context variable called `meta_description`. You might want to use this in, e.g. the `get_context_data` method of a function to set a default for models that do not inherit from SearchMetaBase:

```
{% with meta_description = 'foo' %}
    {{ get_meta_description() }}
{% endwith %}
```

## `get_meta_robots(context, index=None, follow=None, archive=None)`

Renders the content of the meta robots tag for the current page:

{{ get_meta_robots() }}

You can override the meta robots by setting boolean context variables called
``robots_index``, ``robots_archive`` and ``robots_follow``::

```
{% with robots_follow = 1 %}
    {{ get_meta_robots() }}
{% endwith %}
```

You can also provide the meta robots as three boolean arguments to this
tag in the order 'index', 'follow' and 'archive'::

    {{ get_meta_robots(1, 1, 1) }}

## `render_title(browser_title=None)`

Renders the title of the current page::

    {{ render_title }}

You can override the title by setting a context variable called `title`:

```
{% with title = "foo" %}
  {{ render_title() }}
{% endwith %}
```

You can also provide the title as an argument to this tag:

```
{{ title('foo') }}
```

## `render_breadcrumbs(page=None, extended=False)`

Renders the breadcrumbs trail for the current page::

    {{ render_breadcrumbs() }}

To override and extend the breadcrumb trail within page applications, add the ``extended`` flag to the tag and add your own breadcrumbs underneath:

    {{ render_breadcrumbs(extended=1) }}

### How do I....

## ...change the content type after the page has been created?

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

Any objects that have a `ForeignKey` with `on_delete=models.CASCADE` will also be deleted in this case.

If you still want to change the content type, then it's reasonably simple.

#. Go to the create page of the content type you want to change *to*. Copy the number from the ``?type=XX`` portion of the URL.
#. Go to the edit page of the page you wish to switch.
#. Add ``?type=XX`` to the end of the URL.

At this point you will be looking at the fieldset for the new content type, but you will not have applied the changes.  If you're happy with the way your data looks hit Save and the changes will be saved.

## ...change the ModelAdmin ``fieldsets`` of my content model?

Simply add the `fieldsets` tuple to your model rather than your admin.py.

## ...set a `filter_horizontal` on a content model ManyToManyField?

Simply add the ``filter_horizontal`` tuple to your model rather than your admin.py.

## ...add inline model admins to content models?

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

## Media module

The media app provides file and image management to the CMS admin. It also integrates with the CMS's WYSIWYG text editor to provide a file browser and image browser interface that allows images and files to be added directly into the editor.

For images,

### Models

## File

File is a wrapper around a Django FileField. This allows users to upload their files in one place and use it in more than one.

The CMS's `file` provides additional fields: a title, alt text (for images), attribution and copyright. It is up to you how, or if, to render these on the front-end of the website.

## Label

A Label helps administrators organise media; think of them as tags, or notes to self. They are not intended to be shown to users on the front end of a website.

### Fields

To make it easier to integrate the media module into your project, a few fields are provided. You should generally use these any time you want to reference a File.

`FileRefField` provides a widget which allows a user to select a file from the media library. This is a simple subclass of Django's `ForeignKey` that uses Django's `ForeignKeyRawIdWidget` - if you're anything like us, your media libraries can get large enough to make dropdowns unusable).

`ImageRefField` has the same functionality as `FileRefField()`, but files are filtered to only show images. This will also display a small preview of the image in the widget in the admin.

`VideoFileRefField()` has the same functionality as `FileRefField()`, but the files are filtered to only show videos.

## Video

A `Video` model is a collection of video files and related imagery.  You can use it to easily create cross-browser compatible ``<video>`` tags on the frontend of your website.

## Links module (`cms.apps.links`)

The Links module provides a new page content type named "Link" which allows you to have a navigation item without a page associated - it will redirect to an arbitrary URL.

### Configuration

Ensure both ``cms.apps.pages`` and ``cms.apps.links`` are in your project's `INSTALLED_APPS`. If they weren't already, you will need to migrate:

```
$ ./manage.py migrate
```

### Usage

To add a Link to your site simply add a Page.

If you have more than one content type registered (i.e. anything other than that in the Links app itself) you will be asked to choose a page type, after which you choose 'Link'. If you do not have any other page content types you will be taken directly to the add form.  The form itself is very straightforward; simply add the Title for the page and a URL to redirect to.

### Jinja2 template functions

A collection of template tags are included with the pages module, mostly for the purposes of simplifying SEO.

## `render_navigation(pages, section=None)`

Renders the site navigation using the template specified at ``pages/navigation.html``. By default this is just an unordered list with each navigation item as a list item.  The simplest usage is like this::

    {{ render_navigation(pages.homepage.navigation) }}

Which would produce an output like this:

```
<ul>
    <li>
        <a href="/page-1/">Page One</a>
    </li>

    <li>
        <a href="/page-2/">Page Two</a>
    </li>
</ul>
```

If you would like the "base page" (the page that the navigation is being based off) to be included in the navigation simply add the ``section`` kwarg::

```
{{ render_navigation(pages.homepage.navigation, section=pages.homepage) }}
```

The output of this would be:

```
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
```

You will probably want to override the output in your project. For example, you'll almost certainly want to add class names, and to handle children of children. We suggest you make a local copy of `apps/pages/templates/pages/navigation.html` in your project.

## `get_navigation(pages, section=None)`

This is a wrapper around `navigation`, but returns the navigation list instead of rendering it out to the page.

## `get_page_url(page, view_func=None, *args, **kwargs)`

Gets the URL of a Page's view function.

TODO: Expand on this.

## `meta_description(description=None)`

Renders the content of the meta description tag for the current page::

## `get_meta_description()`

You can override the meta description by setting a context variable called `meta_description`. You might want to use this in, e.g. the `get_context_data` method of a function to set a default for models that do not inherit from SearchMetaBase:

```
{% with meta_description = 'foo' %}
    {{ get_meta_description() }}
{% endwith %}
```

## `get_meta_robots(context, index=None, follow=None, archive=None)`

Renders the content of the meta robots tag for the current page:

{{ get_meta_robots() }}

You can override the meta robots by setting boolean context variables called
``robots_index``, ``robots_archive`` and ``robots_follow``::

```
{% with robots_follow = 1 %}
    {{ get_meta_robots() }}
{% endwith %}
```

You can also provide the meta robots as three boolean arguments to this
tag in the order 'index', 'follow' and 'archive'::

    {{ get_meta_robots(1, 1, 1) }}

## `render_title(browser_title=None)`

Renders the title of the current page:

```html
<title>{{ render_title() }}</title>
```

You can override the title by setting a context variable called `title`. This is a silly example

## `render_breadcrumbs(page=None, extended=False)`

Renders the breadcrumbs trail for the current page::

    {{ render_breadcrumbs() }}

To override and extend the breadcrumb trail within page applications, add the ``extended`` flag to the tag and add your own breadcrumbs underneath:

    {{ render_breadcrumbs(extended=1) }}
