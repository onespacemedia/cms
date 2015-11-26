django.jQuery(function($){
    $('.wysiwyg:visible').each(function(){
        activate_tinymce(this)
    });

    Suit.after_inline.register('init_wysiwyg', function(inline_prefix, row){
        $('.wysiwyg:visible', row).each(function(){
            activate_tinymce(this)
        })
    });
})

function activate_tinymce(element){

    // Generate base settings
    var settings = {
      selector: "#" + $(element).attr('id')
    }

    // Merge global settings with base
    $.extend(settings, $(element).data('wysiwyg-settings'))

    // Init editor
    tinymce.init(settings);
}
