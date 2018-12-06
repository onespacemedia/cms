// A bit of a hack to get RawIdForeignKeyFields to work nicely.
// This code overrides the 'Add new' button to use the Jet popup.
(function () {
  document.addEventListener('DOMContentLoaded', function() {
    // Find all the widgets and initialise variables for later
    var rawIdWidgets = document.querySelectorAll('.related-widget-wrapper')
    var currentAddButton = document.querySelector('body')
    var currentLookupButton = document.querySelector('body')

    for (var i = 0; i < rawIdWidgets.length; i++) {
      // Check if the widget is a RawIdForeignKeyField
      if (rawIdWidgets[i].querySelector('.add-related') && rawIdWidgets[i].querySelector('.related-lookup')) {

        currentAddButton = rawIdWidgets[i].querySelector('.add-related')
        currentLookupButton = rawIdWidgets[i].querySelector('.related-lookup')

        // The hack: effectively we override the default behaviour and then
        // run the click event for the item lookup. From there, we wait until
        // the iframe is created for the lookup and them refresh the pop-up
        // iframe with the URL we want for adding a new file.
        currentAddButton.addEventListener('click', function (e) {
          e.preventDefault()
          currentLookupButton.click()
          var checkIframe = window.setInterval(function () {
            if (document.querySelector('.related-popup iframe')) {
              document.querySelector('.related-popup iframe').src = currentAddButton.getAttribute('href')
              window.clearInterval(checkIframe)
            }
          }, 10)
        })
      }
    }
  });
}) ();
