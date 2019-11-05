# A walkthrough

This walkthrough will take you through setting up the CMS on an existing project, and it will introduce several core CMS concepts.
If you prefer to learn from code than learn from a wall of text,
you probably want to look at the companion [tiny CMS project repo](https://github.com/onespacemedia/tiny-cms-project).

## Django settings

We'll need to add a few settings that the CMS depends on.
Don't worry too much about what these do for now; the concepts behind them will be explained in depth over the course of the walkthrough.

First, tell us the name of your site. We depend on this in one of our [template functions](template-functions.md):

```python
SITE_NAME = 'a tiny project'
```

And your domain; it is used by template functions to turn relative /urls/ into http://actual.absolute/urls/:

```python
SITE_DOMAIN = 'example.com'
```

We don't want things set to be offline to appear in the front-end (our pages have on/offline controls), but we definitely want them to appear in our admin:

```python
PUBLICATION_MIDDLEWARE_EXCLUDE_URLS = (
    '^admin/.*',
)
```

Add our core CMS things to your INSTALLED_APPS:

```python
INSTALLED_APPS = [
  # .....
  'cms',
  'cms.apps.pages',
  'cms.apps.media',
  # Links is optional, but it's very handy to have.
  'cms.apps.links',
]
```

Add our context processors to our template context processors (in `['OPTIONS']['context_processors']`):

```python
'cms.apps.pages.context_processors.pages',
```

Add the CMS middleware to your MIDDLEWARE:

```python
MIDDLEWARE = [
  # ...
  'cms.middleware.PublicationMiddleware',
  'cms.apps.pages.middleware.PageMiddleware',
]
```

And finally, options for our HTML editor:

```python
WYSIWYG_OPTIONS = {
    'height': 500,
    'plugins': [
        'advlist autolink link image lists charmap hr anchor pagebreak',
        'wordcount visualblocks visualchars code fullscreen cmsimage hr',
    ],
    'toolbar1': 'code | cut copy pastetext | undo redo | bullist numlist | link unlink anchor cmsimage | blockquote',
    'menubar': False,
    'toolbar_items_size': 'small',
    'block_formats': 'Paragraph=p;Header 2=h2;Header 3=h3;Header 4=h4;Header 5=h5;Header 6=h6;',
    'convert_urls': False,
    'paste_as_text': True,
    'image_advtab': True,
}
```

## Let's make a content model

First, create an app called "content". Assuming that your apps all live in a folder called `apps`, this will do:

```
mkdir apps/content
touch apps/content/__init__.py
```

Now add your `content` app to your `INSTALLED_APPS`.

Then, add this to your `models.py`:

```
from cms.apps.pages.models import ContentBase
from django.db import models


class MyContent(ContentBase):
    introduction = models.TextField(
        null=True,
        blank=True,
    )
```

Let's unpack this!

The `Page` model in the CMS defines its place in the hierarchy, some invisible metadata fields, and some publication controls, and that is it.
It has no opinions about what the _user-visible_ content should look like - not so much as an HTML field!
This is the job of **content models**.

That's what derivatives of `ContentBase` are. Anything that inherits from `ContentBase` will be available as a page type in the CMS.
_There is no explicit registration of content models_; it just works.

<aside>
  We've named this model MyContent.
  In our companion <a href="https://github.com/onespacemedia/tiny-cms-project">tiny CMS project</a>, we've named it simply "Content".
  We use "MyContent" here to avoid confusion between the concept of a "content model", and our model that is named "Content".
</aside>

`introduction` is, of course, a standard Django field, which we'll use this later in our template.
We can define no fields at all on this model! Just its existence as a non-abstract class inheriting from ContentBase will make it available in the page types.

Now go to your admin and add a Page. You will be prompted to select a page type. Once you have selected "My content" as your page type, your page will appear with the `introduction` field all ready to fill out. Do that now, save the page, then go to the root URL on your website.

Surprise! It's totally empty.
Just as it doesn't have any assumptions about what your content looks like, it doesn't have any opinions on what the front end of your site should look like either.
But the CMS is in fact rendering this view, and is making an educated guess as to what template it should use. It's falling back to your `base.html` at the moment, but that's not its first choice. Let's create a template called `content/mycontent.html`:

```
{% extends 'base.html' %}

{% block main %} {# or whatever your main block is on your site :) #}
  <h1>{{ pages.current.title }}</h1>

  <p>{{ pages.current.content.introduction }}</p>
{% endblock %}
```

Now reload your page. It has content! That's because if it hasn't been told to do anything else, it will look for a template at `<app_label>/<model_name>.html`. Convention over configuration ahoy!

Where did `pages` come from? That would be the template context processor you added earlier.
`pages.current` refers to the currently active Page.
`pages.current.content` refers to the instance of your content model that is attached to the page.

This is the very simplest example of rendering a page's content model on the front end.
There's all sorts of other things we can do with content models, but if your model has some fields, and maybe some inlines, you don't _need_ to write any views, just a template.

Did we (royal we) say inlines? We definitely did.

## Lets add some admin inlines

OK, so let's say you want to build your new content page out of an entirely arbitrary number of sections.
That's fine too!
We can add inlines to our change-page view in the admin.
Here is what your model looks like.
Pay special attention to the ForeignKey if nothing else - this is essential, and note that it is to `pages.Page` and _not_ your content model:

```
class ContentSection(models.Model):
    page = models.ForeignKey(
        'pages.Page',
        on_delete=models.CASCADE,
    )

    title = models.CharField(
        max_length=100,
    )

    text = TextField(
        null=True,
        blank=True,
    )

    order = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = ['order']
```

We've defined a section model with a title, text, and an ordering field.
Now let's register it as an inline for MyContent:

```
from cms.apps.pages.admin import page_admin
from django.contrib.admin import StackedInline

from .models import MyContent, ContentSection


class ContentSectionInline(StackedInline):
    model = ContentSection

page_admin.register_content_inline(MyContent, ContentSectionInline)
```

That's it! It's just as easy as adding inlines to any other model.
We've told the CMS "be prepared to display these inlines only when the page type is MyContent".
This won't appear on pages whose type is any other model, because it might not make sense there.

Now, stick this just before the `{% endblock %}` in your `content/mycontent.html` template:

```
{% for section in pages.current.contentsection_set.all() %}
<section>
  <h2>{{ section.title }}</h2>

  {% if section.text %}
    {{ section.text|html}}
  {% endif %}
</section>
{% endfor %}
```

And that concludes part 1: You can now build pages out of an arbitrary number of sections
In fact, for a lot of sites, you might not even need to write a single view!

## Let's make another content model: a deeper dive

For the second part of this walkthrough, we are going to create a simple blog app using some of the CMS's more advanced tooling.

First, create an app called "news", add it to your `INSTALLED_APPS`, and add this to your `news/models.py`:

```
from cms.apps.pages.models import ContentBase

class NewsFeed(ContentBase):

    classifier = 'apps'

    icon = 'icons/news.png'
```

Notice that we're not declaring any model fields here - for now, we won't need to.
Instead, we've introduced two new class attributes that will be used on the "Add a page" screen in your admin: `classifier` and `icon`.

On the "Add a page" screen, the available page types are broken down into classifiers.
Really, this is just a heading under which this page type will appear.
At Onespacemedia we use 'apps' for content models whose primary purpose it is to display links to other content, and 'content' for content models for which the content is primarily on-page.
That's just our convention; you can actually name this anything you like. The CMS doesn't mind!

The `icon` attribute will, as you may have guessed, be displayed in the "Add a page" screen too.
This attribute should be a path inside your static files directory.
The icon itself should be 96x96, but making it a little larger won't hurt.

We don't actually _have_ to specify an icon here; `ContentBase` from which `NewsFeed` inherits has a default icon.
Our news app is super-special, though, so let's give it an icon all its own.
At Onespacemedia we made a whole lot of icons, all in the same style, which are perfect for the 'Add a page' screen.
For now, go grab
[this one](https://github.com/onespacemedia/cms-icons/blob/master/png/news.png)
for your news app and put it in your `static/icons` directory.

This content model will be a news feed, to which articles can be assigned (with a normal `ForeignKey`).
We want to be able to have multiple types of news feed.
For example, we might want to have a page of articles called "News" (what your cat did today) vs "Blog" (insights on cat behaviour).
We'll get to exactly how this will happen shortly.
But first, we're going to need an Article model.

## Let's use the CMS's helper models

The CMS comes with a lot of handy helper models, and some nice helper fields too.
You will want to use them, because you should always use the batteries! We're going to be introducing a couple of them in our `Article` model.

First, add these imports to your `news/models.py`:

```python
from cms.apps.media.models import ImageRefField
from cms.models import HtmlField, PageBase
```

And add the model itself:

```python
class Article(PageBase):
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

OK, let's talk about PageBase here.
It's a helper (abstract) model to make it easier for you to have article-like fields on your model.
It has nearly all the fields that the Page model itself does, but does not consider itself part of any hierarchy.
In fact, the CMS Page itself inherits from PageBase.
Here's what you get (see the [helper models](helpers.md) section for more):

* A title and slug
* Online/offline controls (enforced by the manager)
* OpenGraph and Twitter card fields.
* SEO fields like meta descriptions and a title override.

On to `ImageRefField`.
You can read about the [media app](media-app.md) later on, but the short version is: it's a model wrapper around Django's `FileField`.
`ImageRefField` is a ForeignKey to `media.File`, but it uses a raw ID widget by default, and is constrained to only select files that appear to be images (just a regex on the filename).

`HtmlField` is an HTML field with a nice WYSIWYG editor as its default widget - that was what the `WYSIWYG_OPTIONS` setting was about.
You can use a standard TextField here if you like, or you can bring your own HTML editor; nothing in the CMS requires `HtmlField` to be used.

Now, in our `admin.py` for our news app, we're going to register our Article:

```python
from cms.admin import PageBaseAdmin
from django.contrib import admin

from .models import Article, NewsFeed


@admin.register(Article)
class ArticleAdmin(PageBaseAdmin):
    fieldsets = [
        (None, {
            'fields': ['title', 'slug', 'page', 'content', 'summary'],
        }),
        PageBaseAdmin.PUBLICATION_FIELDS,
        PageBaseAdmin.SEO_FIELDS,
        PageBaseAdmin.OPENGRAPH_FIELDS,
        PageBaseAdmin.OPENGRAPH_TWITTER_FIELDS,
    ]
```

`PageBaseAdmin` defines some useful default behaviour for the article-like things it is intended to enable.
It also defines some useful fieldsets that you will definitely want, such as the publication controls (turning things on/offline), and those SEO and social media controls mentioned earlier.
You should definitely use it for anything that inherits from `PageBase`, but nothing in `onespacemedia-cms` forces you to.

Now, go create a "News feed" page, if you haven't already, and add an Article, setting "Page" to your new news feed.

## Let's add URL routing

We've examined the simple case of how to render a content model using a template.
But what if we want total control over everything under a page's URL?
Like, for example, if we have a page at `/news/`, we want `/news/` to render a list of news articles, and `/news/my-article/` to render the article with the slug `my-article`, but without hard-coding anything in your root urlconf?

Glad you asked! First, let's create a `urls.py` inside your news app, and make it look like this:

```python
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ArticleListView.as_view(), name='article_list'),
    url(r'^(?P<slug>[^/]+)/$', views.ArticleDetailView.as_view(), name='article_detail'),
]
```

You _don't_ want to add this to your root urlconf, because we don't need to.
Instead, add this to your `NewsFeed` model:

```python
urlconf = 'tiny_project.apps.news.urls'
```

You'll want to correct the path; we've assumed your news app lives at `tiny_project.apps.news`.
However you do this, this must be an absolute import path from the root of your Django application.

And there you have it: your page's URLs will now be controlled by your news app's urlconf!
In fact, even the default template-rendering behaviour we visited earlier comes from a default urlconf on ContentBase, which routes to an extremely simple TemplateView derivative.

You'll get an exception thrown now, because we didn't actually implement `news.views`. Let's add a `views.py` in there now:

## Let's access the pages system in a view

```python
from django.views.generic import ListView


class ArticleListView(ListView):
    model = Article

    def get_queryset(self):
        return super().get_queryset().filter(
            page__page=self.request.pages.current
        )

```

This is just a generic Django list view, nothing surprising here.
But we've overridden `get_queryset` so it only returns the articles that have their `page` attribute set to the `NewsFeed` content object of the current page.
We now have multiple news feeds!

Unpacking that `page__page` a bit: the first `page` is the content object, the second is the Page for which it is the content model (content models have a foreign key to Page).

Just like we had access to `pages`, `pages.current`, etc in the context in our template in our first content model example, we have them available in our view, as attributes of the current request.

Let's make a detail view for the article. Add this to your imports:

```python
from cms.views import PageDetailView
```

And make our detail view here:

```python
class ArticleDetailView(PageDetailView):
    model = Article
```

`PageDetailView` is a subclass of Django's `DetailView` that takes care of putting the page title, SEO information and all the other `PageBase` metadata into the template context, where it can be accessed by our CMS's template functions that render them on the page.
If you have a `DetailView` for a model that inherits from `PageBase`, you almost certainly want to inherit from `PageDetailView`, but nothing forces you to.

## Let's reverse some page URLs

Just as a page can define a `urlconf` to render it, that `urlconf` can be reversed any time you have access to a page. It so happens that our Article does: it has a `ForeignKey` to the content model, which has a foreign key to its Page, so we can access it via `self.page.page`.

Like all good models, our article deserves to know what URL it lives at. Let's write a `get_absolute_url` function:

```python
def get_absolute_url(self):
    return self.page.page.reverse('article_detail', kwargs={
        'slug': self.slug,
    })
```

We use `page.reverse` almost exactly like we do Django's `django.urls.reverse`
- in fact, the `reverse` function on Page uses it internally, by passing it the content model's urlconf.

Now that we have a `get_absolute_url` on our news article, we can add a `news/article_list.html` template, where Django's generic `ListView` is expecting to find it:

```
{% extends 'base.html' %}

{% block main %}
  <ul>
    {% for object in object_list %}
      <li>
        <a href="{{ object.get_absolute_url() }}">{{ object.title }}</a>
      </li>
    {% endfor %}
  </ul>
{% endblock %}
```

And now that we can actually make our way to it, an article detail template at `news/article_detail.html`:

```
{% extends 'base.html' %}

{% block main %}
  <h1>{{ object.title }}</h1>

  {% if object.image %}
  <p>
    <img src="{{ object.image.get_absolute_url() }}" alt="">
  </p>
  {{ object.content|safe }}
{% endblock %}
```

## Let's add some per-page settings

Now that we have a news feed, and our cats are writing countless articles about themselves, we'll probably find the need to paginate the news list at some point.
The great part of the simple data model of onespacemedia-cms is that it makes it really easy to define page settings that are not visible to non-admin users.

Add this to our `NewsFeed` content model:

```python
per_page = models.IntegerField(
    verbose_name='articles per page',
    default=12,
)
```

Then, we can override `ListView`'s  `get_paginate_by` in our `ArticleListView`:

```python
  def get_paginate_by(self, queryset):
      return self.request.pages.current.content.per_page

```

There are many use cases for this sort of thing.
If we had a "Contact" content model that rendered a contact form, you could add an `EmailField` to decide who the submissions go to.
Or you may want to make certain `NewsFeed` pages use a different layout; in this case you could add a `layout` field and override `get_template_names` in your view.
There's no need to hard-code anything with onespacemedia-cms!
Some CMSes make this harder for developers than it needs to be; here you're just writing Django.

## Let's add fieldsets to our content model

You may remember that content models do not have `ModelAdmin`s at all - their fields get patched onto the admin form for the _Page_.
But, we like fieldsets! So we simply define them on the NewsFeed content model.
There's no need to list the various SEO and publication fields on the Page here, only ones that our content model has.

```python
fieldsets = [
    ('Settings', {
        'fields': ['per_page'],
    }),
]
```

Of course, this is a silly example as we only have one field on our content model, which doesn't really merit a fieldset.
But it's nice knowing that we have the option if we need it.

## Let's fix your base template

Finally, many times we mentioned about all of that SEO and OpenGraph goodness that would be available in your page's context if we used certain helper models and helper views.
Let's get our template functions into the `<head>` of our document:

```
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

## Next steps

If you haven't already, you'll want to clone the [tiny CMS project](https://github.com/onespacemedia/tiny-cms-project) and have a look around.
It's a slightly-more-fleshed out version of the example we've written here. It has an absurd comment-to-code ratio and serves as a mini walkthrough all by itself.

For a real-world example of much more complex models and views, you might want to look at our [project template](https://github.com/onespacmedia/project-template).

If you're the reading type, you'll want to read [more about the pages system](pages-app.md).
