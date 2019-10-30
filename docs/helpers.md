# Helper models, views, and ModelAdmins

## OnlineBase

`cms.models.OnlineBase` provides publication controls.
It provides a single field: `is_online`. When it is `False` (unchecked), it will not appear on the front-end of your website.

You do not have to do anything other than inherit from OnlineBase for this to work; objects that are not online are automatically excluded from querysets via a custom manager, `OnlineBaseManager`.
We will go into more detail about that later.

`cms.admin.OnlineBaseAdmin` is the companion `ModelAdmin` for this model; derivatives of OnlineBase should probably inherit from this for their user model. It defines `PUBLICATION_FIELDS`, which you can use on your model's admin thusly:

```python
class YourModelAdmin(OnlineBaseAdmin):
    fieldsets = [
        # ... your fieldsets here ...
        OnlineBaseAdmin.PUBLICATION_FIELDS,
    ]
```

`OnlineBaseAdmin` also adds a helpful list `action`: you will be able to turn off items as a batch from the list view.

## PageBase

`cms.models.PageBase` provides the publication control that `OnlineBase` does, but also contains many useful fields that are fairly typical for a typical article-like thing on a website. If an instance of your model lives at its own URL and has a title, such as a news article or a blog post, then you almost certainly want to inherit from `PageBase`. The CMS's own `Page` model inherits from it.

PageBase defines several fields that make this useful for article-like things:

* A title and slug
* SEO controls: title tag override, meta description, robots controls
* Fields for Twitter and Facebook (OpenGraph) cards

`cms.admin.PageBaseAdmin` is the companion `ModelAdmin`; at risk of repeating ourselves, anything that derives from `PageBase` definitely wants to use `PageBaseAdmin`. It prepopulates your `title` and `slug` field automatically, and offers the following fieldsets:

* `PUBLICATION_FIELDS`, inherited from `OnlineBase`
* `SEO_FIELDS` for SEO controls
* `OPENGRAPH_FIELDS`, to control how OpenGraph card rendering (Facebook and others)
* `OPENGRAPH_TWITTER_FIELDS`, to control how Twitter cards are rendered

The companion `cms.views.PageDetailView` is a class-based view that takes care of putting `PageBase` fields into the template context so that they can be seen by the CMS's [template functions](template-functions.md). There is also `cms.views.PageDetailMixin`, which does not inherit from Django's `DetailView`.

Because the Django `DetailView` from which this inherits will check the `slug` kwarg by default, your detail view could be as simple as this:

```python
class ArticleDetailView(PageDetailView):
    model = Article
```

## SearchMetaBase

`cms.models.SearchMetaBase` provides everything that `PageBase` does, except a title and a slug. This is for models in which you want all the features of `PageBase`, but which don't have a "title" from which you can construct a page title.

At Onespacemedia, the most common use for this helper rather than `PageBase` is a typical "people" app, of the kind that would provide an "Our team" page on a typical corporate website. A person model does not have a title; they'll [typically](https://www.kalzumeus.com/2010/06/17/falsehoods-programmers-believe-about-names/) have at least a first name, a last name, and some other name fields from which you can construct a page title.

`cms.admin.SearchMetaBaseAdmin` is the same as `PageBaseAdmin`, but does not have the title and prepopulated slug.

`cms.views.SearchMetaDetailView` is the companion class-based detail view, which, similarly, only differs from `PageDetailView` in that there is no title to put into the page context. Should you need to use `SearchMetaDetailView`, you will want to ensure the key 'title' is in the template context.

## Managers

As mentioned in `OnlineBaseManager`, anything that inherits from `OnlineBase` will have a manager that ensures that objects with `is_online == False` will be excluded from `Model.objects.all()`.
For `OnlineBase` this is `cms.models.OnlineBaseManager`, for `PageBase` it is `cms.models.PageBaseManager`, etc.

<aside>
PageBaseManager and SearchMetaBaseManager inherit from OnlineBaseManager, and do not currently add any features. But if you inherit from PageBase you should probably inherit from PageBaseManager in case extra features get added to the corresponding helper models.
</aside>

It will only return offline objects in a queryset if any of the following things are true:

* The current request's user is a staff user, _and_ the `preview` GET parameter in the URL is non-empty (e.g. `?preview=1`). This allows administrators to preview offline objects.
* The current request's path matches a regular expression in the `settings.PUBLICATION_URLS` tuple. One of these will probably be `^admin/` in your configuration, for obvious reasons.

Sometimes you might want to exclude objects automatically based on other criteria.
Take the Article model in the [walkthrough](walkthrough.md); we might want to exclude any Article with a future publication date, to allow building a publication queue.
Rather than having to remember to filter the articles everywhere they are used, now and in the future (your news list, [sitemaps](sitemaps.md), etc), we can inherit from `PageBaseManager` to ensure that they are excluded _everywhere_ (other than in the circumstances detailed above):

```python
from cms.models import PageBase, PageBaseManager
from django.utils.timezone import now


class ArticleManager(PageBaseManager):
    def select_published(self, queryset):
        return super().select_published(queryset).exclude(date__gt=now())


class Article(PageBase):
    objects = ArticleManager()

    # ... your model fields here ...
```

There is also a `PublishedBaseManager` that you can override in exactly the same way, in case you are not inheriting from one of the helper models (thus don't have an `is_online` field) but still have criteria under you would always like objects to be hidden on the front-end of the site.
This is how the [moderation system](moderation.md) works.
