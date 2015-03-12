if (!RedactorPlugins) var RedactorPlugins = {};

(function($) {
    RedactorPlugins.filemanager = function() {
        return {
            init: function() {
                this.modal.addCallback('file', this.filemanager.load);
            },
            load: function() {
                var $modal = this.modal.getModal();

                this.modal.createTabber($modal);
                this.modal.addTab(1, 'Upload', 'active');
                this.modal.addTab(2, 'Choose');

                $('#redactor-modal-file-upload-box').addClass('redactor-tab redactor-tab1');

                var $box = $('<div id="redactor-file-manager-box" style="overflow: auto; height: 300px;" class="redactor-tab redactor-tab2">').hide();
                var $file_container = $('<div id="redactor-file-manager-files"></div>')
                var $pagination_container = $('<div id="redactor-file-manager-pagination"></div>')

                $box.append($file_container);
                $box.append($pagination_container);
                $modal.append($box);

                $.proxy(this.filemanager.load_files(), this)

            },
            load_files: function(page) {

                $.ajax({
                    dataType: "json",
                    cache: false,
                    url: '/admin/media/file/redactor/files/' + (page == undefined ? '1' : page) + '/',
                    success: $.proxy(function(data) {

                        // Empty file manager
                        $('#redactor-file-manager-files').html('');

                        var ul = $('<ul id="redactor-modal-list">');
                        $.each(data.objects, $.proxy(function(key, val) {
                            var a = $('<a href="#" title="' + val.title + '" rel="' + val.url + '" class="redactor-file-manager-link">' + val.title + ' </a>');
                            var li = $('<li />');

                            a.on('click', $.proxy(this.filemanager.insert, this));

                            li.append(a);
                            ul.append(li);

                        }, this));

                        $('#redactor-file-manager-files').append(ul);

                        // We can set up pagination
                        $.proxy(this.filemanager.load_pagination(data.page, data.pages), this)

                    }, this)
                });
            },
            load_pagination: function(page, pages) {
                // Empty image pagination
                $('#redactor-file-manager-pagination').html('');

                // Loop pages
                if (pages.length > 1) {
                    pages.forEach($.proxy(function(value, key) {

                        // Create page link
                        var page_link = $('<a href="#" class="' + (value == page ? 'active' : '') + '">' + value + '</a>');

                        // Add page link to pagination container
                        $('#redactor-file-manager-pagination').append(page_link);

                        // On page click, load new page with new pagination
                        page_link.click($.proxy(function() {
                            $.proxy(this.filemanager.load_files(value), this)
                        }, this))

                    }, this))
                }
            },
            insert: function(e) {
                e.preventDefault();

                var $target = $(e.target).closest('.redactor-file-manager-link');

                this.file.insert('<a href="' + $target.attr('rel') + '">' + $target.attr('title') + '</a>');
            }
        };
    };
})(django.jQuery);
