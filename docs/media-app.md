# The Media app

## User-visible features

The media app provides file and image management to the Django admin.
It also integrates with the CMS's WYSIWYG text editor to provide a file browser and image browser interface that allows images and files to be added directly into the editor.

The default `FileAdmin` adds a thumbnail preview to the list view, falling back to an appropriate icon for the file type if the file is not an image.

For images, there is an in-browser image editor that gives quick access to common image operations such as cropping and rotating.

## Models

### File

`cms.apps.media.models.File` is a wrapper around a Django FileField. This allows users to upload their files in one place and use it in more than one place.

The CMS's `File` provides additional fields: a title, alt text (for images), attribution and copyright. It is up to you how, or if, to render these on the front-end of the website.

`File` is not typically used for files uploaded via the public front-end of a website (i.e. non-staff users). For this, you'll want to use a simpler Django `FileField` or `ImageField`.

### Label

`cms.apps.media.models.Label` helps administrators organise media; think of them as tags, or notes to self. They are not intended to be shown to users on the front end of a website.

### Video

`cms.apps.media.models.Video` is a collection of video files and related imagery.  You can use it to easily create cross-browser compatible ``<video>`` tags on the frontend of your website.

## Fields

A few fields are provided To make it easier to integrate the media module into your project. You should generally use these any time you want to reference a File.

`FileRefField` provides a widget which allows a user to select a file from the media library. This is a simple subclass of Django's `ForeignKey` that uses Django's `ForeignKeyRawIdWidget` - if you're anything like us, your media libraries can get large enough to make dropdowns unusable.

`ImageRefField` has the same functionality as `FileRefField()`, but files are filtered to only show images. This will also display a small preview of the image in the widget in the admin.

`VideoFileRefField()` has the same functionality as `FileRefField()`, but the files are filtered to only show videos.

