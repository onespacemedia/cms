# Sitemaps

Any model that has a `get_absolute_url()` method should probably have its URL exposed in an [XML sitemap](https://en.wikipedia.org/wiki/Sitemaps) for easier indexing by search engines.
The CMS has some helpers for this, which build on Django's [sitemaps framework](https://docs.djangoproject.com/en/dev/ref/contrib/sitemaps/).

First, you will need a URL route in your root `urls.py`. You will want something very much like this:

```python
from cms.sitemaps import registered_sitemaps
from django.contrib.sitemaps import views as sitemaps_views

urlpatterns = [
    # ...your URLS here...
    url(r'^sitemap.xml$', sitemaps_views.index, {'sitemaps': registered_sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^sitemap-(?P<section>.+)\.xml$', sitemaps_views.sitemap, {'sitemaps': registered_sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
```

There are, of course, helper sitemap classes for all of the CMS's [helper models](helpers.md).
You don't need to worry about those much of the time.
The `cms.sitemaps.register` function guesses an appropriate one for you:

```python
from cms import sitemaps
sitemaps.register(YourModel)
```

It will guess which sitemap class to use based on which helper model your model inherits from,
checking `PageBase`, `SearchMetaBase`, and `OnlineBase`, in that order.

`cms.sitemaps.BaseSitemap` does not do anything at all, other than returning all of the instances of a given model.
It assumes that the model implements a `get_absolute_url` method.

`cms.sitemaps.OnlineBaseSitemap` is for models that inherit from OnlineBase.
It will ensure that objects that are not online (`is_online == False`) will not be shown in the sitemap.
Actually, it simply inherits from `BaseSitemap` and adds nothing - it is the manager on `OnlineBase` that ensures only online objects are shown.
But if you are inheriting from `OnlineBase` your sitemap should inherit from this class in case this implementation detail changes in the future.

`cms.sitemaps.SearchMetaBaseSitemap` and `cms.sitemaps.PageBaseSitemap` are for models that inherit from `SearchMetaBase` and `PageBase`.
It will add the change frequency and priority from the SEO fields on those models to the model's sitemap.
It will also exclude any objects that have been excluded from search engines (i.e. `robots_index == False`).

It may be useful to exclude certain URLs from your sitemap on criteria other than its "online" status.
Let's contrive an example.
Say you have an `Article` model in your site that inherits from `PageBase`, which has the option of just linking to an external URL, rather than having any content of its own.
We don't want those articles to appear in the sitemap. So we exclude them from indexing like so.

```python
from cms import sitemaps

class ArticleSitemap(sitemaps.PageBaseSitemap):
    model = Article

    def items(self):
        return super().items().filter(external_url=None)

sitemaps.register(Article, sitemap_cls=ArticleSitemap)
```

Once you have a sitemap, you will want search engines to know where it lives.
Add an entry like this to your /robots.txt:

```
Sitemap: https://www.example.com/sitemap.xml
```
