django.jQuery(function($){
    setTimeout(() => {
        $('.wysiwyg:visible').each(function(){
            activate_tinymce(this)
        });
    }, 250)

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
    django.jQuery.extend(settings, $(element).data('wysiwyg-settings'))

    // Init editor
    tinymce.init(settings);
}
