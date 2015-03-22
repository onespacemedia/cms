Media Module
============

The media app provides a file and image management interface to the CMS admin. It also integrates with WYSIWYG text editors to provide a file browser and image browser interface that allows images and files to be uploaded directly into the editor.

Models
------

To make it easier to integrate the media module into your project a selection of models are provided.

.. py:class:: FileRefField()

Provides a widget which allows a user to select a file from the media library.

.. py:class:: ImageRefField()

The same functionality as the ``FileRefField()``, but with the files filtered to only show images.

.. py:class:: VideoFileRefField()

The same functionality as the ``FileRefField()``, but with the files filtered to only show videos.

.. py:class:: VideoRefField()

A ``Video`` object is a collection of video files and related imagery.  You can use it to easily create cross-browser compatible ``<video>`` tags on the frontend of your website.
