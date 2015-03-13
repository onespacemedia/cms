if (!RedactorPlugins) var RedactorPlugins = {};

(function($) {
    RedactorPlugins.imagemanager = function() {
        return {
            init: function() {
                this.modal.addCallback('image', this.imagemanager.load);
            },
            load: function() {
                var $modal = this.modal.getModal();

                this.modal.createTabber($modal);
                this.modal.addTab(1, 'Upload', 'active');
                this.modal.addTab(2, 'Choose');

                $('#redactor-modal-image-droparea').addClass('redactor-tab redactor-tab1');

                var $box = $('<div id="redactor-image-manager-box" style="overflow: auto; height: 300px;" class="redactor-tab redactor-tab2">').hide();
                var $image_container = $('<div id="redactor-image-manager-images"></div>')
                var $pagination_container = $('<div id="redactor-image-manager-pagination"></div>')

                $box.append($image_container);
                $box.append($pagination_container);
                $modal.append($box);

                $.proxy(this.imagemanager.load_images(), this)

            },
            load_images: function(page) {

                $.ajax({
                    dataType: "json",
                    cache: false,
                    url: '/admin/media/file/redactor/images/' + (page == undefined ? '1':page) + '/',
                    success: $.proxy(function(data) {

                        // Empty image manager
                        $('#redactor-image-manager-images').html('');

                        // Loop objects in data
                        $.each(data.objects, $.proxy(function(key, val) {

                            // Create the image
                            var img = $('<img src="' + val.thumbnail + '" rel="' + val.url + '" title="' + val.title + '" style="height: 75px; cursor: pointer;" />');

                            // Add the image to the manager box
                            $('#redactor-image-manager-images').append(img);

                            // On image click, insert the image into the wysiwyg
                            $(img).click($.proxy(this.imagemanager.insert, this));

                        }, this));

                        // We can set up pagination
                        $.proxy(this.imagemanager.load_pagination(data.page, data.pages), this)

                    }, this)
                });
            },
            load_pagination: function(page, pages) {
                // Empty image pagination
                $('#redactor-image-manager-pagination').html('');

                // Loop pages
                if(pages.length > 1) {
                    pages.forEach($.proxy(function(value, key) {

                        // Create page link
                        var page_link = $('<a href="#" class="' + (value == page ? 'active' : '') + '">' + value + '</a>');

                        // Add page link to pagination container
                        $('#redactor-image-manager-pagination').append(page_link);

                        // On page click, load new page with new pagination
                        page_link.click($.proxy(function() {
                            $.proxy(this.imagemanager.load_images(value), this)
                        }, this))

                    }, this))
                }
            },
            insert: function(e) {
                this.image.insert('<img src="' + $(e.target).attr('rel') + '" alt="' + $(e.target).attr('title') + '">');
            }
        };
    };
})(django.jQuery);
