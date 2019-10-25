# django-watson integration

## Helper search adapters

## Controlling search text for content models (ContentBase derivatives)

By default, PageSearchAdapter will add all textual fields (CharField, TextField and anything that inherits from it) to the blob of text that gets indexed (with a lower priority than the page title). That's sensible behaviour, but you may have inlined models that need to be searched too. For example, our simple sectioned content model from the [walkthrough](walkthrough.md) has most of its textual content in `ContentSection` models. Those are rendered on the page, so it makes sense for that text to be searchable.

If your content model has textual content in related models in this way, or in fields that do not inherit from `CharField` or `TextField`), you can override `get_searchable_text`. Here is how you would do it for the model in the walkthrough:

FIXME: this is entirely untested

```python
def get_searchable_text(self):
    text = super().get_searchable_text()
    return ' '.join([text] + [
        section.title + ' ' (section.text or '')
        for section in self.page.contentsection_set.all()
    ])
```

