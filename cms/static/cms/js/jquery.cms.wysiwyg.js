function activate_tinymce(element){
  var settings = {
    selector: "#" + element.getAttribute('id')
  }

  // Merge per-editor settings
  var inlineSettings = JSON.parse(element.dataset.wysiwygSettings)
  for (var key in inlineSettings) {
    if (inlineSettings.hasOwnProperty(key)) {
      settings[key] = inlineSettings[key];
    }
  }

  tinymce.init(settings);
}
