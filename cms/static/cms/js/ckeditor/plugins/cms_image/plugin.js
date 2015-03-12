(function() {

    CKEDITOR.plugins.add('cms_image', {
        icons: 'cms_image',
        init: function(editor) {

            editor.addCommand('cms_image', new CKEDITOR.dialogCommand('cms_image_dialog'));

            editor.ui.addButton('CMS Image', {
                label: 'CMS Image',
                command: 'cms_image',
                toolbar: 'insert',
                icon: 'cms_image'
            });

            CKEDITOR.dialog.add('cms_image_dialog', this.path + 'dialogs/cms_image.js');

        }
    });

    CKEDITOR.on('dialogDefinition', function(event) {
        window.active_ckeditor = event.editor

        // When the cms_image_dialog dialog is opened
        if (event.data.name == 'cms_image_dialog') {
            var dialog = CKEDITOR.dialog.getCurrent();
            console.log(dialog)
        }
    });

})();
