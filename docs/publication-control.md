# Publication control

As mentioned in `OnlineBase` in our discussion about [helper models](helpers.md), anything that inherits from `OnlineBase` will have a manager that ensures that objects with `is_online == False` will be excluded from `Model.objects.all()`.
For `OnlineBase` this is `cms.models.OnlineBaseManager`, for `PageBase` it is `cms.models.PageBaseManager`, etc.

?> **Note:** PageBaseManager and SearchMetaBaseManager inherit from OnlineBaseManager, and do not currently add any features.
But if your model inherits from PageBase or SearchMetaBase,
a custom manager for it should inherit from the corresponding manager,
in case extra features get added to the helper model and/or manager.

It will only return offline objects in a queryset if _any_ of the following things are true:

* The current request's user is a staff user, _and_ the `preview` GET parameter in the URL is non-empty (e.g. `?preview=1`). This allows administrators to preview offline objects.
* The value of the `preview` GET parameter matches a hash of the current path and your `settings.SECRET_KEY` (this is a simplification of, but not entirely unlike, how it actually works). This is used by `OnlineBase` to implement its `get_preview_url()` method.
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


## Bypassing the publication manager

It is sometimes desirable to bypass the publication controls under certain circumstances.
For example, if a non-admin user has posted a news article that needs to be approved by an admin, you might still want to show it in a list of their own articles.

You can do this by importing `cms.models.publication_manager` and using its `select_published` context manager:

```python
from cms.models import publication_manager

# ...

with publication_manager.select_published(False):
    return YourModel.objects.all()
```

## Next steps

Read about the [moderation system](moderation.md), which is built on `PublishedBaseManager`.
