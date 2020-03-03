# Changelog

## Next release
* Add fix for duplicating the homepage.

## 4.4.3 - 2020-03-03
* Remove the site name from the page title by default.

## 4.4.2 - 2020-01-24
* Fix issue with LocalisationMiddleware where it would throw an exception if the IP didn't belong to a country.

## 4.4.1 - 2020-01-08
* Fix missed change to `handle_uncaught_exception` in Django 2.2 compatability update.

## 4.4.0 - 2019-12-05
* Django 2.2 compatibility is now complete:
  * **Breaking change:** If you are using `LocalisationMiddleware`, change your `MIDDLEWARE_CLASSES` setting to `MIDDLEWARE`. The other CMS middleware is now compatible with both, but the check for localisation middleware now only looks at `MIDDLEWARE`, to simplify 2.2 compatibility.
  * **Breaking change:** `cms` must now be in your `INSTALLED_APPS`.
  * **Breaking change:** localised sites now use `geoip2` - you will need to [update your GeoIP database](https://dev.maxmind.com/geoip/geoip2/downloadable/).
  * All `ForeignKey`s now have an `on_delete` explicitly specified (one was missed in 4.2.0).

## 4.3.1 - 2019-12-04
* The [documentation](https://onespacemedia.github.io/cms/) has been completely rewritten.

## 4.3.0 - 2019-11-12
* Importing `cms.sitemaps` at the top level of a module containing an app's AppConfig no longer raises `AppRegistryNotReady`.
* `PageBase`'s help text for the `slug` field now makes sense.
* `OnlineBase` and its derivatives (including the Page model) now implement `get_preview_url()`, to generate a URL at which non-admin users can preview an object.
* Remove a pessimisation in `PageManager.get_homepage`.

## 4.2.0 - 2019-11-06
* Show usage of media library files on the file's change form.
* Make middleware compatible with both `MIDDLEWARE` and `MIDDLEWARE_CLASSES`.
* Ensure all `ForeignKey`s have an `on_delete` explicitly specified for Django 2.2 compatibility.
* Rename "Search engine optimization" fieldset of SearchMetaBaseAdmin to "SEO".

## 4.1.0 - 2019-10-25
* Make it possible for ContentBase derivatives to override how they are searched by Watson.

## 4.0.10 - 2019-10-18
* Fix `Video.embed_html()` function using the wrong renderer for local mp4 files.
* Remove `cached_url` from the Page model, because it is [unreliable](https://github.com/onespacemedia/cms/pull/181).

## 4.0.9 - 2019-10-11
* Remove key press listeners from image editor
* Fix an issue where get parameters in the URL made saving a new page impossible

## 4.0.8 - 2019-09-18
* Don't override `submit_line.html` - this should be a decision for the CMS skin or a project-local override.

## 4.0.7 - 2019-09-18
* Simplify template override for `pages/page/change_form.html`.

## 4.0.6 - 2019-09-19
* Fix saving pages from the changelist view when its content model has `fieldsets` under certain circumstances.
* Restore ordering of media library to be most recent first.

## 4.0.5 - 2019-09-03
* Add a class to the ImageRefField widget's image preview to allow for easier styling.

## 4.0.4 - 2019-08-27
* Fix an issue when changing page ContentType where the new ContentType has ManyToMany fields not on the original.

## 4.0.3 - 2019-08-08
* Big speedups in RequestPageManager.

## 4.0.2 - 2019-08-06
* Fix migration state.

## 4.0.1 - 2019-07-26
* Fix issue for multilingual site and offline pages [[See #176](https://github.com/onespacemedia/cms/pull/176/files)]

## 4.0.0 - 2019-07-26
* Decouple from django-suit
* Massive code clean up
* In admin image editing for media app

## 2.0.0 - 2016-10-03
* Switched to Jinja2 as the template engine.
