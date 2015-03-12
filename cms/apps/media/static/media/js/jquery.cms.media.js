/*
    TinyMCE filebrowser implementation.
*/


(function($) {

    // Define the filebrowser plugin.
    $.cms.media = {}

    // Closes the filebrowser and sends the information back to the TinyMCE editor.
    $.cms.media.complete = function(permalink, title) {

        // Insert an image
        window.parent.window.active_ckeditor.insertHtml('<img src="' + permalink + '" title="' + title + '" />');

        // Close the dialog
        window.parent.CKEDITOR.dialog.getCurrent().hide()

    }

    // Initializes the popup file browser.
    $.cms.media.initBrowser = function() {
        if (parent.window.active_ckeditor) {
            // Make the changelist links clickable and remove the original inline click listener.
            $("div#changelist tr.row1 a, div#changelist tr.row2 a").attr("onclick", null).click(function() {
                var img = $("img", this);
                var title = img.attr("title");
                var permalink = img.attr("cms:permalink");
                $.cms.media.complete(permalink, title)
                return false;
            });
            // Made the add link flagged for CKEditor.
            $(".object-tools a").attr("href", $(".object-tools a").attr("href") + "&_ckeditor=1");
        }
    }

    // Add in the filebrowser plugin to the rich text editor.
    $.fn.cms.htmlWidget.extensions.file_browser_callback = function(field_name, url, type, win) {
        var browserURL = "/admin/media/file/?_popup=1";
        if (type == "image") {
            browserURL = browserURL + '&file__iregex=\x5C.(png|gif|jpg|jpeg)$';
        }
        if (type == "media") {
            browserURL = browserURL + '&file__iregex=\x5C.(swf|flv|m4a|mov|wmv)$';
        }
        tinyMCE.activeEditor.windowManager.open({
            file: browserURL,
            title: "Select file",
            width: 800,
            height: 600,
            resizable: "yes",
            inline: "yes",
            close_previous: "no",
            popup_css: false
        }, {
            window: win,
            input: field_name,
            tinymce_active: true
        });
        return false;
    }

}(django.jQuery));
