# Helper models, views, and ModelAdmins

## OnlineBase

`cms.models.OnlineBase` provides publication controls.
It provides a single field: `is_online`.
An object with this field set to `False` (unchecked) will not appear on the front-end of your website.

You do not have to do anything other than inherit from OnlineBase for this to work; objects that are not online are automatically excluded from querysets via a custom manager, `OnlineBaseManager`.
We will go into more detail about that [elsewhere](publication-control.md).

`OnlineBase` implements a `get_preview_url()` method that generates a secret URL at which an object can be previewed by non-administrative users.
We use this in our [OSM Jet](https://github.com/onespacemedia/osm-jet) admin skin to generate a "click to copy public preview URL" function.
If your model does not implement a `get_absolute_url()` method, this method will return `None`.

`cms.admin.OnlineBaseAdmin` is the companion `ModelAdmin` for this model;
if your model inherits directly from `OnlineBase`, your `ModelAdmin` should inherit from `OnlineBaseAdmin`.
It defines `PUBLICATION_FIELDS`, which you can use on your model's admin like this:

```python
class YourModelAdmin(OnlineBaseAdmin):
    fieldsets = [
        # ... your fieldsets here ...
        OnlineBaseAdmin.PUBLICATION_FIELDS,
    ]
```

`OnlineBaseAdmin` also adds a helpful list `action`: you will be able to turn off items as a batch from the list view.

By default, new objects will have the checkbox for `is_online` checked by default in the admin, if your `ModelAdmin` extends from `OnlineBase`.
If you want to change this, set `ONLINE_DEFAULT` to `False` in your Django settings.

## PageBase

`cms.models.PageBase` provides the publication control that `OnlineBase` does, but also contains many useful fields that are useful for page- or article-like models on a website.
If an instance of your model lives at its own URL and has a title, such as a news article or a blog post, then you almost certainly want to inherit from `PageBase`.
The CMS's own `Page` model inherits from it.

PageBase defines several fields that make this useful for article-like things:

* A title and slug
* Search engine optimisation (SEO) controls: title tag override, meta description, robots controls
* Fields for Twitter and Facebook (OpenGraph) cards

`cms.admin.PageBaseAdmin` is the companion `ModelAdmin`; anything that derives from `PageBase` definitely wants to use `PageBaseAdmin`.
It prepopulates your `title` and `slug` field automatically, and offers the following fieldsets:

* `PUBLICATION_FIELDS`, inherited from `OnlineBase`
* `SEO_FIELDS` for SEO controls
* `OPENGRAPH_FIELDS`, to control how OpenGraph card rendering (Facebook and others)
* `OPENGRAPH_TWITTER_FIELDS`, to control how Twitter cards are rendered

The companion `cms.views.PageDetailView` is a class-based view that takes care of putting `PageBase` fields into the template context so they are seen by the CMS's [template functions](template-functions.md).
There is also `cms.views.PageDetailMixin`, which does the same thing but does not inherit from Django's `DetailView`.

Because the Django `DetailView` from which this inherits will check the `slug` kwarg by default, your detail view could be as simple as this:

```python
class ArticleDetailView(PageDetailView):
    model = Article
```

## SearchMetaBase

`cms.models.SearchMetaBase` provides everything that `PageBase` does, except a title and a slug.
This is for models in which you want all the features of `PageBase`, but which don't have a "title" from which you can construct a page title.

At Onespacemedia, the most common use for this helper rather than `PageBase` is a typical "people" app, of the kind that would provide an "Our team" page on a typical corporate website.
A person model does not have a title; they'll [typically](https://www.kalzumeus.com/2010/06/17/falsehoods-programmers-believe-about-names/) have at least a first name, a last name, and some other name fields from which you can construct a page title.

`cms.admin.SearchMetaBaseAdmin` is the same as `PageBaseAdmin`, but does not have the title and prepopulated slug.

`cms.views.SearchMetaDetailView` is the companion class-based detail view, which, similarly, only differs from `PageDetailView` in that there is no title to put into the page context.
Should you need to use `SearchMetaDetailView`, you will want to ensure the key 'title' is in the template context.

## Next steps

Read about how [publication control](publication-control.md) works on these models.
