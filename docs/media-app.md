# The Media app

The media app provides file and image management to the Django admin.
It also integrates with the CMS's WYSIWYG text editor to provide a file browser and image browser interface that allows images and files to be added directly into the editor.

## Models

### File

`cms.apps.media.models.File` is a wrapper around a Django FileField.
This allows users to upload a file in one place and use it in more than one place.

`File` is not intended for files uploaded via the public front-end of a website (i.e. non-staff users).
For this, you'll want to use a simpler Django `django.db.models.FileField` or `ImageField`.

The default `FileAdmin` adds a thumbnail preview to the list view, falling back to an appropriate icon for the file type if the file is not an image.

For images, there is an in-browser image editor that gives quick access to common image operations such as cropping and rotating.

The admin will show a list of all the places where an object is used in a "Usage" fieldset, with links (where possible) to their admin URLs.
It's smart enough to know about usage within inlines, both those registered to normal models and as inlines on [content models](pages-app.md).

When uploading images, an attempt is made to guard against a file being uploaded with an extension that does not match its contents.
For example, you won't be able to upload a PNG file with a `.jpg` extension, or vice-versa.
This helps to prevent exceptions being thrown while thumbnailing images on the front-end of the site.

#### Model fields

* `title`: A name for the file.
In the admin, this is prepopulated from the filename when first uploaded, if no title is provided by the user.
* `labels`: A `ManyToManyField` to `Label` (see below).
* `file`: A Django `FileField`, which is the file itself.
* `attribution`, `copyright` and `alt_text`: Additional metadata fields.
It is up to you how, or if, to render these on the front end of the site.

In addition, the following fields are present on the model, but are not user-visible and are automatically populated on save:

* `width` and `height`: The image dimensions of the file, if the file is an image.
* `date_added`: The time the file was first uploaded. This is used for ordering in the admin (most recent first).

#### Model methods & properties

* `get_dimensions()`: If the file is an image, returns a tuple of (width, height), otherwise returns 0.
This is only used internally; you probably want to access the `width` and `height` fields on the model instead, as they incur no overhead.
* `icon`: A cached property that returns the path to an appropriate icon for the file type, e.g. `/static/media/img/x-office-spreadsheet.png`. This is used as a fallback in the media list if a file is not an image.
* `is_image()`: Returns True if the file is an image (based on the file extension), False otherwise:

### Label

`cms.apps.media.models.Label` helps administrators organise media;
think of them as tags, or notes to self.
The are not intended to be shown to users on the front end of a website.

Label has only one field: a `title`, which is also used as the ordering field.

### Video

`cms.apps.media.models.Video` is a collection of video files and related imagery.
You can use it to easily create cross-browser compatible `<video>` tags on the frontend of your website.

It has the following fields:

* `title` is self-explanatory.
* `external_video` is for embedding an off-site video (e.g. YouTube, Vimeo, etc). More on this below.
* `high_resolution_mp4` is for a self-hosted MP4 (H.264). This is a `VideoFileRefField`, which is a reference to a `media.File`.
* `low_resolution_mp4` for a lower-resolution version suitable for playing on mobile devices.
* `image` is for displaying a cover image on the video (e.g. for the `poster` attribute on the `<video>` tag).

For external videos, the `save` method on the model will work out how to embed the video.
If the video has oEmbed information, some hidden fields will be populated that you can use on your front end to embed it:

* `external_video_id` will be the provider's ID for the video.
For YouTube, this will be a string of seemingly-random characters (e.g. `3LlAi8ygeMI`), or a number for Vimeo videos.
* `external_video_iframe_url` will be populated with the URL of the IFrame (presuming that this is how your video provider embeds it, which all major ones do).
For a YouTube video, an example would be `https://www.youtube.com//embed/3LlAi8ygeMI?feature=oembed`.
* `external_video_provider` is the lower-case name of the provider, e.g. `youtube`.

If the external video does not provide oEmbed information
(e.g. because the uploader has prevented embedding, or the service does not support oEmbed),
`ValidationError` will be raised.

The `Video` model provides the `embed_html` method to intelligently provide embed HTML for your video.
You can pass it the `loop`, `autoplay`, `controls`, `mute` parameters to control playback & appearance, all of which default to `False`.
Additionally, for YouTube external videos, you can pass it `youtube_parameters`, which will be added as query string parameters to the embed IFrame.
For example, if you wish to enable the YouTube JS API on an embed, you can pass `{'enablejsapi': '1'}`.

## Fields

Three useful fields in the media app make it easier to integrate the media module into your project.
You should probably use these any time you want to reference a File.

`cms.apps.media.models.FileRefField` provides a widget which allows a user to select a file from the media library.
This is a simple subclass of Django's `ForeignKey` that uses Django's `ForeignKeyRawIdWidget` -
if you're anything like us, your media libraries can get large enough to make dropdowns unusable.

`cms.apps.media.models.ImageRefField` has the same functionality as `FileRefField`, but files are filtered to only show images (based on the extension of the file).
This will also display a small preview of the image in the widget in the admin.

`cms.apps.media.models.VideoFileRefField` has the same functionality as `FileRefField`, but the files are filtered to only show videos.
