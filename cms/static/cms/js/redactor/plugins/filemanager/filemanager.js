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

                var $box = $('<div id="redactor-file-manager" style="overflow: auto; height: 600px;" class="redactor-tab redactor-tab2">').hide();
                var $iframe = $('<iframe src="/admin/media/file/?_popup=1$" width="100%" height="580" frameborder="0"></iframe>');
                $iframe.appendTo($box);
                $modal.append($box);

                window.active_redactor = this.filemanager

            },
            insert: function(src, title) {
                this.file.insert('<a href="' + src + '">' + title + '</a>');
            }
        };
    };
})(django.jQuery);
