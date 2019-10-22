# Helper models, views, and `ModelAdmin`s

## OnlineBase

`cms.models.OnlineBase` provides publication controls. It provides a single field: `is_online`. When it is `False` (unchecked), it will not appear on the front-end of your website.

You do not have to do anything other than inherit from OnlineBase for this to work; objects that are not online are automatically excluded from querysets via a custom manager (`OnlineBaseManager`).

Because this custom manager is aware of the currently active request, it will return offline objects in a queryset if any of the following things are true:

* The current request's user is a staff user, _and_ the `preview` GET parameter in the URL is non-empty (e.g. `?preview=1`). This allows you to preview offline objects.
* The current request's path matches a regular expression in the `settings.PUBLICATION_URLS` tuple. One of these will probably be `^admin/` in your configuration, for obvious reasons.

## PageBase

`cms.models.PageBase` provides the publication control that `OnlineBase` does, but also contains many useful fields that are fairly typical for a typical article-like thing on a website. If an instance of your model lives at its own URL and has a title, then you almost certainly want to inherit from `PageBase`. The CMS's own `Page` model inherits from it.

TODO:
* SEO fields
* OG/Twitter fields
* `PageBaseAdmin`
* `PageDetailMixin`

## SearchMetaBase

`cms.models.SearchMetaBase` provides everything that `PageBase` does, except a title and a slug. This is for models in which you want all the features of `PageBase`, but which don't have a "title" from which you can construct a page title.

At Onespacemedia, the most common use for this helper rather than `PageBase` is a typical "people" app, of the kind that would provide an "Our team" page on a typical corporate website. A person model does not have a title; they'll [typically](https://www.kalzumeus.com/2010/06/17/falsehoods-programmers-believe-about-names/) have at least a first name, a last name, and some other name fields from which you can construct a page title.

TODO:
* `SearchMetaAdminMixin`
* `SearchMetaBaseAdmin`
