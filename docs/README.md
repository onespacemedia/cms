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
