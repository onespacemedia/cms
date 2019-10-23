# Walkthrough

temporary: smooshed together from some comments on tiny-cms-project

## Django settings

## Base template changes

## Let's make a content model

```
from cms.apps.pages.models import ContentBase

class NewsFeed(ContentBase):
    classifier = 'apps'

    icon = 'icons/news.png'

    intro_text = models.TextField(
        default='Welcome to my blog!',
    )
```

On the "Add a page" screen, the available page types are broken down into classifiers.
Really, this is just a heading under which this page type will appear.
Typically, at Onespacemedia we use 'apps' for content models whose primary purpose it is to display links to other content, and 'content' for content models for which the content is primarily on-page.
That's just our convention; you can actually name this anything you like. The CMS doesn't mind!

This will be title-cased when it is rendered in the admin.

icon:

```
An icon at this location (under your static files directory) will be
displayed in the "Add a page" screen. ContentBase has a default icon,
but you can make your own icons too. This should be 96x96 at the moment,
but making it a little larger wouldn't hurt.

For now, go grab
[this one](https://github.com/onespacemedia/cms-icons/blob/master/png/news.png)
for your news app and stick it into your `static/icons` directory.
Need some help? At Onespacemedia we made a whole lot of icons in the
same style which are perfect for the 'Add a page' screen.
```


## Let's use the CMS's helper models

```
from cms.models import PageBase
```

```
class Article(PageBase):
    '''A simple news article.'''

    page = models.ForeignKey(
        'news.NewsFeed',
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        verbose_name='News feed'
    )

    image = ImageRefField(
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    content = HtmlField()

    date = models.DateTimeField(
        default=now,
    )

    summary = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title
```



We want to be able to have multiple types of news feed. For example,
we might want to have a page of articles called "News" (what your cat
did today) vs "Blog" (insights on cat behaviour). Because we have access
to the current page and its content object in our request, we can filter
only the news articles which have this ForeignKey set to the currently
active page - alternatively put, that "belong" to it.



ImageRefField is a ForeignKey to `media.File`, but it uses a raw ID
widget by default, and is constrained to only select files that appear
to be images (just a regex on the filename). You also have FileRefField
that doesn't do the "looks like an image" filtering, but does use the
raw ID widget.

The urlconf used to power this content's views. We don't *have* to
specify this at all! If we did not then it would simply render a
template at <app_label>/<model_name>.html. But this allows us to have
have complete control of everything below this page in the URL
structure.

In fact, even the default view mentioned above comes from a urlconf on
ContentBase, with an extremely simple TemplateView derivative.


```
urlconf = 'tiny_project.apps.news.urls'
```

```
    def get_absolute_url(self):
        # OK, so once we have our urlconf on our content object, whereever we
        # we have access to that content, we reverse those URLs almost exactly
        # as we use django's standard reverse.
        #
        # self.page here is our NewsFeed (content model), and self.page.page
        # is the page to which our content model is attached.
        return self.page.page.reverse('article_detail', kwargs={
            'slug': self.slug,
        })
```

## Per-page-type URL routing

## Using the pages system in a view

```
class ArticleListView(ListView):
    model = Article

    def get_queryset(self):
        # As also mentioned in models.py, we only want to list those news
        # articles that "belong" to the current page. Once again, our
        # PageMiddleware and its friend RequestPageManager make this really
        # easy.
        return super().get_queryset().filter(
            page__page=self.request.pages.current
        )
```

## Adding per-page settings

Now that

```
    per_page = models.IntegerField(
        verbose_name='Articles per page',
        default=12,
    )
```

And on to some model fields.
The great part of the simple data model of onespacemedia-cms is that it makes it really easy to define page settings that are not visible to non-admin users.
Here, we want admin
control over how many will be displayed on a page. We'll be able to
access this later in the `get_paginate_by` function in our view.
Another typical example would be deciding where a form on a "Contact"

content model would send emails to. No need to hard-code anything! Some
other CMSes make this extraordinarily hard; here you're just writing
Django.

Notice also that onespacemedia-cms works perfectly with standard Django model fields.


```
    def get_paginate_by(self, queryset):
        # As mentioned in models.py, we have a simple setting on the content
        # model to control how many news articles are being shown by page
        # (just a plain old IntegerField). In there, we mentioned that we
        # would have access to the current page in the view. But how?
        #
        # Simples: PageMiddleware patches the current page tree on to the
        # request (actually an instance of RequestPageManager).
        # `pages.current` is the currently active page, i.e. the page to which
        # our current content object is attached. So all we need to do to make
        # it paginate by our admin-defined amount is...
        return self.request.pages.current.content.per_page

```
## Adding fieldsets to our content model

```
    fieldsets = [
        ('Settings', {
            'fields': ['per_page'],
        }),
    ]
```

comment:
```
    # ContentBase derivatives don't have ModelAdmins at all - their fields get
    # automatically patched into the form for the *Page*. But, we like
    # fieldsets! So we simply define them on the model. There's no need to
    # list the various SEO and publication fields on the Page here; these will
    # be added automatically.
```

## Let's make another content model

## Next steps

If you haven't already

For a real-world example of much more complex models and views, you might want to look at our [project template](https://github.com/onespacmedia/project-template).
