function activate_tinymce (element) {
  // Generate base settings
  var settings = {
    selector: "#" + element.getAttribute('id')
  }

  // Merge global settings with base
  django.jQuery.extend(settings, JSON.parse(element.dataset.wysiwygSettings))

  // Init editor
  tinymce.init(settings);
};

(function ($) {
  window.addEventListener('load', function () {
    function activateEditors() {
      $('.wysiwyg:visible').each(function (){
          activate_tinymce(this)
      });
    }
    window.setTimeout(activateEditors, 100)
    // Reactivate on Jet tab change.
    window.addEventListener('hashchange', activateEditors)
  })
})(django.jQuery);
