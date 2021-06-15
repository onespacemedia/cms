# Changelog

## 5.0.2 - 2021-06-15
* Add migrations that get added on Django 3.2 projects from `DEFAULT_AUTO_FIELD` changes

## 5.0.1 - 2021-05-19
* Add missing migration merge

## 5.0.0 - 2021-05-19
* Add versioning to pages

## 4.4.23 - 2021-05-19
* Add duration field to Videos
* Display schema on non-local videos

## 4.4.22 - 2021-05-12
* Add missing mark_safe import

## 4.4.21 - 2021-05-12
* Fix issue with schema json generation

## 4.4.20 - 2021-04-19
* Adjust `media.Video` templates to render both low and high res video files. Add support for poster images on local videos.
* Add schema for local videos.

## 4.4.19 - 2021-03-26
* Update SEO fields to match industry standard terms for title and meta.

## 4.4.18 - 2021-03-18
* Fix VideoRefFields throwing an error if, in the returned JSON, 'title' wasn't provided.

## 4.4.17 - 2021-02-25
* Fix VideoRefFields throwing an error if, in the returned JSON, 'provider_name' wasn't provided.

## 4.4.16 - 2021-01-15
* Fix issue with incorrect version being published.

## 4.4.15 - 2021-01-15
* Fix issue where checking if user was authenticated was being called incorrectly.

## 4.4.14 - 2020-12-15
* Remove TinyPNG from media app

## 4.4.13 - 2020-11-2
* Get image dimensions during a pre_save signal instead of saving the file twice.

## feature/middleware-updates
* Update middleware to no longer use deprecated MiddlewareMixin
* Remove redundant code from middleware + general code cleanup
* Change pages system to use PageDispatcher view as its entry point
* Fix confusing options for Country.default
* LOCALISATION_MIDDLEWARE_EXCLUDE_URLS is a new setting

## 4.4.12 - 2020-11-2
* Use the media storage `.open()` function to retrieve an image instead of `open()`

## 4.4.11 - 2020-10-30
* Fix issue where adding a file would error with remote storages.
* Fix issue where list page would error if a remote storage was being used

## 4.4.10 - 2020-10-28
* Have the media storage class extend the current default storage class

## 4.4.9 - 2020-09-16
* Increase max length of page slugs to 150

## 4.4.8 - 2020-08-27
* Update PageAdmin to fully validate the fields on related Content objects

## 4.4.7 - 2020-08-25
* Fix issue with page base Twitter cards for summary_large_image

## 4.4.6 - 2020-08-20
* Fix bug with media.File.embed_html where controls on vimeo embeds are inverse to provided values.
* Fix bug where oembed information would fail to be collected on Vimeo videos due to being blocked by a Captcha

## 4.4.5 - 2020-04-07
* Allow a setting to determine if the media library overfiles files on the disk or preserves them.
* Increase the max slug length of pages

## 4.4.4 - 2020-03-03
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
