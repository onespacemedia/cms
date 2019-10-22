# Onespacemedia CMS documentation

Onespacemedia CMS is a collection of Django extensions that add content-management facilities to Django projects, originally forked from [etianen/cms](https://github.com/etianen/cms). The team at [Onespacemedia](http://www.onespacemedia.com>) are actively working on the project, adding new features, updating existing ones and keeping it working with the latest versions of Django.

The current version of onespacemedia-cms should always be compatible with the current LTS version of Django.

## Requirements

Onespacemedia CMS assumes Jinja2 templating with [django-jinja](https://github.com/niwinz/django-jinja), search with [django-watson](https://github.com/etianen/django-watson/issues), and very little else.

## Features

onespacemedia-cms comes with very few features by default. It has no opinions about how your project should work, it has minimal opinions about how the admin looks, and it plays well with your existing models.

-  Hierarchal page management with no depth limit.
-  Publication controls with online preview.
-  Pre-configured WYSIWYG editor widgets (using TinyMCE)
-  Image and file management, with easy embedding via WYSIWYG editors or pure model fields.
-  Internal / external links in menus (via bundled `links` app).
-  Version control and rollback (via [django-reversion](https://github.com/etianen/django-reversion)).
-  Automatic SEO-friendly redirect management (via [django-historylinks](https://github.com/etianen/django-historylinks)).
-  Full-text search with relevance ranking (via [django-watson](https://github.com/etianen/django-watson)).
-  Many helper model classes and views for SEO-friendly user-visible models.

## Getting started

### Project template

Onespacemedia's [project template](https://github.com/onespacemedia/project-template) is the fastest way to get a new project started with onespacemedia-cms. It includes a set of basic apps, many useful helper functions & classes, and a front-end build system based on Node, Webpack and PostCSS. See the instructions in the [GitHub repository](https://github.com/onespacemedia/project-template>) for details.

### Installation on an existing project

To install `onespacemedia-cms` simply run:

```
$ pip install onespacemedia-cms
```

Add the CMS to your `INSTALLED_APPS`:

```
INSTALLED_APPS = [
    ...
    'cms',
    'cms.apps.pages',
    'cms.apps.media',
    'cms.apps.links',
]
```

Add the page middleware:

```
MIDDLEWARE = [
    ...
    'cms.middleware.PublicationMiddleware',
    'cms.apps.pages.middleware.PageMiddleware',
]
```

Finally, add `cms.apps.pages.context_processors.pages` to your template engine's `context_processors`.


You should now run the following:

```
$ ./manage.py migrate
```

## Pages module


The ``pages`` module is a standard CMS module which allows users to add pages to the website. However, it does not do anything by itself; It requires you to add models into your project which inherit from `cms.apps.ContentBase`

### How it works

In `cms.apps.pages.models` there is a model named `Page`, which contains a set of generic page fields such as `parent`, `publication_date`, ``expiry_date`` and so on.

To be able to add a ``Page`` to the site, we need a content model.  A content model is a way of representing a type of page. This could be a homepage, a standard page, a contact page etc -- each content model would have its own front-end template thus allowing you to provide different layout types, themes etc throughout your site.

Here is an example of a content model::


```
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

If we wanted to have another page type with a different set of fields (or even the same fields) we simply have to add another model which extends ``ContentBase``, like so::

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

### Context processor

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

### Jinja2 template functions

A collection of template tags are included with the pages module, mostly for the purposes of simplifying SEO.

#### `render_navigation(pages, section=None)`

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

#### `get_navigation(pages, section=None)`

This is a wrapper around `navigation`, but returns the navigation list instead of rendering it out to the page.

#### `get_page_url(page, view_func=None, *args, **kwargs)`

Gets the URL of a Page's view function.

TODO: Expand on this.

#### `meta_description(description=None)`

Renders the content of the meta description tag for the current page::

#### `get_meta_description()`

You can override the meta description by setting a context variable called `meta_description`. You might want to use this in, e.g. the `get_context_data` method of a function to set a default for models that do not inherit from SearchMetaBase:

```
{% with meta_description = 'foo' %}
    {{ get_meta_description() }}
{% endwith %}
```

#### `get_meta_robots(context, index=None, follow=None, archive=None)`

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

#### `render_title(browser_title=None)`

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

#### `render_breadcrumbs(page=None, extended=False)`

Renders the breadcrumbs trail for the current page::

    {{ render_breadcrumbs() }}

To override and extend the breadcrumb trail within page applications, add the ``extended`` flag to the tag and add your own breadcrumbs underneath:

    {{ render_breadcrumbs(extended=1) }}

### FAQs

#### Can I change the content type after the page has been created?

Yes, but it has risks.  Changing the content type will cause you to lose data in any fields which don't exist in the new model, that is to say that if your structure looks like this::

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

#### Can I change the ModelAdmin ``fieldsets`` of a model admin view?

Yes. Simply add the ``fieldsets`` tuple to your model rather than your admin.py.

#### Can I set a ``filter_horizontal`` on a content model ManyToManyField?

Yes. Simply add the ``filter_horizontal`` tuple to your model rather than your admin.py.

#### Can I add inline model admins to content models?

Yes. First, you need to add a ForeignKey from your inline model to `pages.Page` (note: *not* your content model!).

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

#### File

File is a wrapper around a Django FileField. This allows users to upload their files in one place and use it in more than one.

The CMS's `file` provides additional fields: a title, alt text (for images), attribution and copyright. It is up to you how, or if, to render these on the front-end of the website.

#### Label

A Label helps administrators organise media; think of them as tags, or notes to self. They are not intended to be shown to users on the front end of a website.

##### `is_image`

### Fields

To make it easier to integrate the media module into your project, a few fields are provided. You should generally use these any time you want to reference a File.

`FileRefField` provides a widget which allows a user to select a file from the media library. This is a simple subclass of Django's `ForeignKey` that uses Django's `ForeignKeyRawIdWidget` - if you're anything like us, your media libraries can get large enough to make dropdowns unusable).

`ImageRefField` has the same functionality as `FileRefField()`, but files are filtered to only show images.

`VideoFileRefField()` has the same functionality `FileRefField()`, but the files are filtered to only show videos.

#### VideoRefField()

A `Video` object is a collection of video files and related imagery.  You can use it to easily create cross-browser compatible ``<video>`` tags on the frontend of your website.

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


## Moderation plugin

Built into the CMS is a moderation system which allows any model in your project to be controlled by a status system.  Models which utilise the moderation system gain a field named `status` which has three possible values: "Draft", "Submitted for approval" or "Approved". Objects are only visible on the front-end of the website when they are marked as "Approved".

Adding the moderation system to a model will create a new permission to be created named "Can approve items". Users will need to have this permission to be able to publish items to the website by setting the object status to "Approved", users without the permission will only be able to set the object status to "Draft" or "Submitted for approval".

### Adding the moderation system to a model

There are a few steps required to integrate the moderation system with your models.  You will need to modify your models.py to look like this:

```
from cms.plugins.moderation.models import ModerationBase

class MyModel(ModerationBase):

    # If you wish to set Meta settings, you need to extend ModerationBase.Meta.
    class Meta(ModerationBase.Meta):
        pass
```

To integrate the moderation system with the Django admin system modify your admin.py to use this structure:

````
from cms.plugins.moderation.admin import MODERATION_FIELDS, ModerationAdminBase
from django.contrib import admin

from .models import MyModel


@admin.register(MyModel)
class MyModelAdmin(ModerationAdminBase):
    fieldsets = [
        MODERATION_FIELDS,
    ]
```

If your model already existed before adding the moderation system you will need to run `./manage.py update_permissions` (and probably restart the server) before they appear.
