// A bit of a hack to get RawIdForeignKeyFields to work nicely.
// This code overrides the 'Add new' button to use the Jet popup.
(function () {
  window.addEventListener('load', function () {
    django.jQuery(document).on('click', '.add-related', function (event) {
      var $target = django.jQuery(event.target);
      // Find all the widgets and initialise variables for later
      var $rawIdWidget = $target.closest('.related-widget-wrapper');

      // Don't assume that it's present!
      if (!$rawIdWidget.length) {
        return;
      }

      var $lookupButton = $rawIdWidget.find('.related-lookup');
      var $addButton = $rawIdWidget.find('.add-related');

      if (!$addButton.length || !$lookupButton.length) {
        return
      }
      event.preventDefault()

      // The hack: effectively we override the default behaviour and then
      // run the click event for the item lookup. From there, we wait until
      // the iframe is created for the lookup and them refresh the pop-up
      // iframe with the URL we want for adding a new file.
      var checkIframe = window.setInterval(function () {
        if (document.querySelector('.related-popup iframe')) {
          document.querySelector('.related-popup iframe').src = $addButton.attr('href')
          window.clearInterval(checkIframe)
        }
      }, 10)
      $lookupButton[0].click()
    });
  });
}) ();
