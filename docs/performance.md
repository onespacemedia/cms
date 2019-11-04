# Notes on performance

onespacemedia-cms is extremely performant.

The baseline overhead of the CMS (the pages middleware, rendering the navigation, and accessing a page's content model) is significantly less than 100 milliseconds in local development for a typical mid-sized website with no caching.
A typical production configuration is faster than this.

If your time-to-first-byte performance is suffering, it is likely that your site is badly optimised elsewhere.
Read the [Django documentation](https://docs.djangoproject.com/en/dev/topics/performance/) for ideas as to why your performance is being hurt.

The CMS itself has a couple of notable performance pitfalls, which are easy to avoid.

## Page.content is not free (the first time)

Accessing the `content` property of a page causes at least one database query, and sometimes two.
Because it is a [cached property](https://docs.djangoproject.com/en/dev/ref/utils/#django.utils.functional.cached_property),
future accesses of it are close to free, but your first access of it is not.

Treating it as free might be damaging your performance.
An example might be your navigation template's implementation of the `new_window` field of the [Link content model](links-app.md).
If you check against `page.content.new_window` in every item in your navigation, you will cause at _least_ one extra database query for every single item in your navigation.
For a large site, this can have quite some performance impact.

Your solution is to only check against `Page.content` when you know you need to.
In the example above, you could put the `Link` model's content type ID into your page's context, with a context processor like this:

```python
def page_type_ids(request):
    # Imports need to be here because this can cause an apps-not-ready
    # exception.
    from cms.apps.links.models import Link
    from django.contrib.contenttypes.models import ContentType

    return {
        'page_type_ids': {
            'link': ContentType.objects.get_for_model(Link).id,
            # more page types here if you need to check against their
            # `.content` too
        }
    }
```

That way, you could check against `page.content_type_id` to see if its content type is a `Link`, and only access `page.content.new_window` if it is:

```
<a href="{{ entry.url }}" itemprop="url" {% if entry.page.content_type_id == page_type_ids.link and entry.page.content.new_window %}target="_blank"{% endif %}>
   {{ entry.title }}
</a>
```

## Expensive 404 pages

Because the pages middleware only attempts to render a page at a given URL when the URL would 404 otherwise, your 404 page is rendered before the page is served.
Therefore, if your 404 page is expensive to render, all pages on your site will be expensive to render too.
In particular, rendering your navigation in your 404 page causes the navigation to be rendered _twice_ - once for the 404 page, once for the navigation itself. This almost doubles the CMS's baseline overhead!

For better results, strip down your 404 page to its absolute minimum.
