# django-watson integration

Onespacemedia CMS integrates [django-watson](https://github.com/etianen/django-watson) into the admin for improved full-text searching of pages in your admin.
Any ModelAdmin that inherits from the `SearchMetaBaseAdmin` or `PageBaseAdmin` [helper ModelAdmins](helpers.md) will also get this full-text search.

As much as we like Watson, the CMS does not require that you use Watson for searching on the front-end of your site;
you're free to implement your own search, or no search at all.
If you choose to use Watson on your front-end, and you are using the CMS's helper models, the CMS supplies a few helper search adapters.
Just pass one of these as the second argument to `register` (see ["Registering models"](https://github.com/etianen/django-watson/wiki/registering-models) in Watson's documentation):

```
from cms.models import OnlineBaseSearchAdapter

watson.register(YourModel, OnlineBaseSearchAdapter)
```

`cms.models.OnlineBaseSearchAdapter`, from this example, is used to register models that inherit directly from `OnlineBase`.
It ensures that objects that are set as offline do not appear in your search results.

`cms.models.PageBaseSearchAdapter` is for models that inherit from `PageBase`.
It will ensure that the title of an object (rather than its `__str__`) is used as its title in search results.
An object's meta description will be used as the description of its search result.
It inherits the behaviour of `OnlineBaseSearchAdapter` above, but will also exclude any results that have been excluded from external search engine crawlers.

`cms.models.SearchMetaBaseSearchAdapter` is for models that inherit directly from the less-commonly-used `SearchMetaBase`.
It behaves exactly like `PageBaseSearchAdapter`, but doesn't assume the presence of a "title" field;
it will default to Watson's behaviour of using the `__str__` of the object as the title in search results.

## Controlling search text for content models (ContentBase derivatives)

The CMS `Page` model is registered with `cms.apps.pages.models.PageSearchAdapter` by default. `PageSearchAdapter` will add all textual fields from the page's content object to the blob of text that gets indexed (with a lower priority than the page title).

That's sensible behaviour, but you may have inlined models that need to be searched too.
For example, our simple sectioned content model from the [walkthrough](walkthrough.md) has most of its textual content in `ContentSection` objects.
Those are rendered on the page, so that text should be searchable.

If your content model has textual content in related models in this way, or in fields that do not inherit from `CharField` or `TextField`, you can override `get_searchable_text` on your content model.
Here is how you would do it for the `Content` model in the walkthrough:

```python
def get_searchable_text(self):
    text = super().get_searchable_text()
    return ' '.join([text] + [
        section.title + ' ' + (section.text or '')
        for section in self.page.contentsection_set.all()
    ])
```

## Avoiding "&lt;content model&gt; matching query does not exist" during page save

If you are creating a Page outside of the admin (such as in unit tests), you will probably get an exception warning that your page's content does not exist.
This is because of the page's search adapter looking for `get_searchable_text` on the content;
it is calling the cached property `.content` on the Page instance to fetch the page's content, which does not and cannot exist until the page itself has been saved.

To work around this, you will want to wrap it in Watson's `search.update_index` context manager:


```python
from watson import search


with search.update_index():
    new_page = Page(
        # your page creation fields here
    )

    new_page.save()

    SomeContentModel.objects.create(
        page=new_page,
    )
```
