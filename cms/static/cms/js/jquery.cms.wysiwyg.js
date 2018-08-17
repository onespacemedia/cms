function activate_tinymce(element){
    // Generate base settings
    var settings = {
      selector: "#" + element.getAttribute('id')
    }

    // Merge global settings with base
    var inline_settings = JSON.parse(element.dataset.wysiwygSettings)
    for(var key in inline_settings)
        if(inline_settings.hasOwnProperty(key))
            settings[key] = inline_settings[key];

    // Init editor
    tinymce.init(settings);
}
