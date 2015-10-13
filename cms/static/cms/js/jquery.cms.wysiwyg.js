django.jQuery(function($){
    $('.wysiwyg:visible').each(function(){
        $(this).ckeditor($(this).data('wysiwyg-settings'));

        $(this).ckeditor().on('instanceReady.ckeditor', function(event, editor){

            // Output self-closing tags the HTML4 way, like <br>.
            editor.dataProcessor.writer.selfClosingEnd = '>';

            // Use line breaks for block elements, tables, and lists.
            var dtd = CKEDITOR.dtd;
            for (var e in CKEDITOR.tools.extend({}, dtd.$nonBodyContent, dtd.$block, dtd.$listItem, dtd.$tableContent)) {
                editor.dataProcessor.writer.setRules(e, {
                    indent: true,
                    breakBeforeOpen: true,
                    breakAfterOpen: true,
                    breakBeforeClose: true,
                    breakAfterClose: true
                });
            }
        });

    });

    Suit.after_inline.register('init_wysiwyg', function(inline_prefix, row){
        $('.wysiwyg:visible', row).each(function(){
            $(this).ckeditor($(this).data('wysiwyg-settings'));
        })
    });


})
