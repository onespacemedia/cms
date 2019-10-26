# Changelog

## 4.1.0 - 25/10/2019
* Make it possible for ContentBase derivatives to override how they are searched by Watson.

## 4.0.10 - 18/10/2019
* Fix `Video.embed_html()` function using the wrong renderer for local mp4 files.
* Remove `cached_url` from the Page model, because it is [unreliable](https://github.com/onespacemedia/cms/pull/181).

## 4.0.9 - 11/10/2019

* Remove key press listeners from image editor
* Fix an issue where get parameters in the URL made saving a new page impossible

## 4.0.8 - 18/09/2019

* Don't override `submit_line.html` - this should be a decision for the CMS skin or a project-local override.

## 4.0.7 - 18/09/2019

* Simplify template override for `pages/page/change_form.html`.

## 4.0.6 - 18/09/2019

* Fix saving pages from the changelist view when its content model has `fieldsets` under certain circumstances.
* Restore ordering of media library to be most recent first.

## 4.0.5 - 03/09/2019

* Add a class to the ImageRefField widget's image preview to allow for easier styling.

## 4.0.4 - 27/08/2019

* Fix an issue when changing page ContentType where the new ContentType has ManyToMany fields not on the original.

## 4.0.3 - 08/08/2019

* Big speedups in RequestPageManager.

## 4.0.2 - 06/08/2019

* Fix migration state.

## 4.0.1 - 26/07/2019

* Fix issue for multilingual site and offline pages [[See #176](https://github.com/onespacemedia/cms/pull/176/files)]

## 4.0.0 - 26/07/2019

* Decouple from django-suit
* Massive code clean up
* In admin image editing for media app

## 2.0.0 - 03/10/2016

* Switched to Jinja2 as the template engine.

1.0.5.1 - 29/08/2014
--------------------
