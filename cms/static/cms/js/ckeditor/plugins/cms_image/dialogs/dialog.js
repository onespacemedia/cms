CKEDITOR.dialog.add('cms_image_dialog', function(editor) {
    return {
        title: 'Image',
        minWidth: 400,
        minHeight: 200,
        contents: [
            {
                id: 'tab-media-app',
                elements: [
                    {
                        type: 'iframe',
                        id: 'mediaAppFrame',
                        src: '/admin/media/file/?_popup=1&file__iregex=.(png|gif|jpg|jpeg)$',
                        width: '700px',
                        height: '500px',
                    }
                ]
            },
        ]
    };
});
