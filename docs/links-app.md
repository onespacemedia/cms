# The Links app

The Links module provides a content model named "Link" which allows you to have a navigation item without any page content associated;
instead, its navigation entry will redirect to an arbitrary URL.

## Configuration

Ensure both `cms.apps.pages` and `cms.apps.links` are in your project's `INSTALLED_APPS`. If they weren't already, you will need to migrate:

```
$ ./manage.py migrate
```

## Usage

To add a Link to your site simply add a Page and select the "Link" page type.

If you have more than one content type registered (i.e. anything other than that in the Links app itself) you will be asked to choose a page type, after which you choose 'Link'.
If you do not have any other page content types you will be taken directly to the add form.
The form itself is very straightforward; simply add the Title for the page and a URL to redirect to.

You can control what kind of redirect is used with the `permanent` boolean field.
It defaults to being off, i.e. it will use a 302 Found (temporary) redirect.

There is a 'New window' field, which is an instruction to open the link in a new window. This does nothing by itself; you will need to handle this in your navigation template.
