CKEDITOR.plugins.add('cms_image', {
    init: function(editor) {
        editor.addCommand('cms_image', new CKEDITOR.dialogCommand('cms_image_dialog'));

        editor.ui.addButton('CmsImage', {
            label: 'Insert CMS Image',
            command: 'cms_image',
            toolbar: 'insert'
        });

        CKEDITOR.dialog.add('cms_image_dialog', this.path + 'dialogs/dialog.js');
    }
});

CKEDITOR.on('dialogDefinition', function (e) {
    if(e.data.name == 'cms_image_dialog'){
        e.data.definition.dialog.on('show', function () {
            window.active_ckeditor = e.editor;
            window.active_ckeditor_dialog = e.data.definition.dialog;
        })
    }
});
