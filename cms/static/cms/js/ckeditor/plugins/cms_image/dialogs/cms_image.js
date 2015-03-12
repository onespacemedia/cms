(function() {
    CKEDITOR.dialog.add('cms_image_dialog', function(editor) {
        return {
            title: 'CMS Image',
            width: 800,
            height: 600,
            contents: [
                {
                    id: 'iframe',
                    label: 'Basic Settings',
                    expand: true,
                    elements: [
                        {
                            type: 'iframe',
                            width: '800',
                            height: '600',
                            src: '/admin/media/file/?_popup=1&file__iregex=.(png|gif|jpg|jpeg)$',
                        }
                    ]
                }
            ],
            show: function(event){
            }
        };
    });
})();
