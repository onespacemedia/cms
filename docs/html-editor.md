# The HTML editor

Onespacemedia CMS comes with a <abbr title="What You See Is What You Get">WYSIWYG</abbr> HTML editor that you can use on your models to provide rich-text editing in your admin using TinyMCE v4.
The CMS does not use this internally (as it has no opinions about what your content should look like),
but it's included with the CMS because almost every website requires it.

First, you will want to provide some settings for TinyMCE using the `WYSIWYG_OPTIONS` setting.
These correspond to [TinyMCE v4's settings](https://www.tiny.cloud/docs-4x/configure/integration-and-setup/).

Here is a nice minimal configuration:

```python
WYSIWYG_OPTIONS = {
    # Overall height of the WYSIWYG
    'height': 500,

    # The one to pay attention to here is `cmsimage` - it allows you to insert
    # images from your media library.
    'plugins': [
        'advlist autolink link image lists charmap hr anchor pagebreak',
        'wordcount visualblocks visualchars code fullscreen cmsimage hr',
    ],
    # cmsimage here gives you the aforementioned item in your toolbar.
    'toolbar1': 'code | cut copy pastetext | undo redo | bullist numlist | link unlink anchor cmsimage | blockquote',
    'menubar': False,
    'toolbar_items_size': 'small',
    'block_formats': 'Paragraph=p;Header 2=h2;Header 3=h3;Header 4=h4;Header 5=h5;Header 6=h6;',
    'convert_urls': False,
    'paste_as_text': True,
    'image_advtab': True,
}
```

Adding the `cmsimage` plugin (and corresponding `cmsimage` button) will allow media files to be inserted directly from your [media gallery](media-app.md).

Next, use `cms.models.HtmlField` to add HTML editing to your admin.
`HtmlField` is a subclass of `TextField` which overrides the widget with a TinyMCE text editor.
Other than the widget, it works just like a `TextField`:

```python
from cms.models import HtmlField
# ... other imports here ....


class Article(models.Model)
    content = HtmlField()
```

That's it!

When rendering the HTML on the front-end of your site, you probably want to filter your HTML through the `html` template filter.
This will expand permalinks and set alt text, attribution etc on the images in your WYSIWYG editor (if they were inserted through the media library plugin mentioned above).

```
{{ object.content|html }}
```

There may be circumstances in which you want to use the HTML editing widget, but not use `HtmlField` on your model.
In this unusual case, use `cms.fields.HtmlWidget` in your form class.
