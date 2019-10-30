# Jinja2 template functions

A collection of template functions are included with the pages module, mostly for the purposes of simplifying SEO.

## TL;DR

The `<head>` of your document should look like this:

```
<meta name="description" content="{{ get_meta_description() }}">
<meta name="robots" content="{{ get_meta_robots() }}">
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

## Page metadata functions

### `render_title(browser_title=None)`

Renders the title of the current page:

```
{{ render_title() }}
```

You can override the title by setting a context variable called `title`:

```
{% with title = "foo" %}
  {{ render_title() }}
{% endwith %}
```

### `meta_description(description=None)`

Renders the content of the meta description tag for the current page:

```
<meta name="description" value="{{ get_meta_description() }}">
```

You can override the meta description by setting a context variable called `meta_description`. You might want to use this in, e.g. the `get_context_data` method of a function to set a default for models that do not inherit from SearchMetaBase:

```
{% with meta_description = 'foo' %}
  {{ get_meta_description() }}
{% endwith %}
```

### `get_meta_robots(context, index=None, follow=None, archive=None)`

Renders the content of the meta robots tag for the current page:

```
{{ get_meta_robots() }}
```

You can override the meta robots by setting boolean context variables called
``robots_index``, ``robots_archive`` and ``robots_follow``:

```
{% with robots_follow = 1 %}
  {{ get_meta_robots() }}
{% endwith %}
```

You can also provide the meta robots as three boolean arguments to this
tag in the order 'index', 'follow' and 'archive':

```
{{ get_meta_robots(1, 1, 1) }}
```

## Navigation functions
### `render_navigation(pages, section=None)`

Renders the site navigation using the template specified at ``pages/navigation.html``. By default this is just an unordered list with each navigation item as a list item.  The simplest usage is like this:

```
{{ render_navigation(pages.homepage.navigation) }}
```

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

If you would like the "base page" (the page that the navigation is being based off) to be included in the navigation simply add the ``section`` kwarg:

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

### `render_breadcrumbs(page=None, extended=False)`

Renders the breadcrumbs trail for the current page:

```
{{ render_breadcrumbs() }}
```

To override and extend the breadcrumb trail within page applications, add the ``extended`` flag to the tag and add your own breadcrumbs underneath:

```
{{ render_breadcrumbs(extended=1) }}
```

### `get_page_url(page, view_func=None, *args, **kwargs)`

Gets the URL of a Page's view function.

TODO: Expand on this.
