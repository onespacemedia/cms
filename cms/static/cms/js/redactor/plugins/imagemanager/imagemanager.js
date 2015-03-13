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

                var $box = $('<div id="redactor-image-manager" style="overflow: auto; height: 600px;" class="redactor-tab redactor-tab2">').hide();
                var $iframe = $('<iframe src="/admin/media/file/?_popup=1&file__iregex=.(png|gif|jpg|jpeg)$" width="100%" height="580" frameborder="0"></iframe>');
                $iframe.appendTo($box);
                $modal.append($box);

                window.active_redactor = this

            },
            insert: function(src, title) {
                this.image.insert('<img src="' + src + '" alt="' + title + '">');
            }
        };
    };
})(django.jQuery);
