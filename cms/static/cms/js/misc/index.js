// {# A bit of a hack to get RawIdForeignKeyFields to work nicely.   #}
// {# This code overrides the 'Add new' button to use the Jet popup. #}
// {# This is here as opposed to the CMS so it's avaliable on every  #}
// {# page.                                                          #}
(function () {
  document.addEventListener('DOMContentLoaded', function() {
//  {# Find all the widgets and initialise variables for later #}
    var rawIdWidgets = document.querySelectorAll('.related-widget-wrapper')
    var currentAddButton = document.querySelector('body')
    var currentLookupButton = document.querySelector('body')

//  {# iterate over the widgets on the page #}
    for (var i = 0; i < rawIdWidgets.length; i++) {
//    {# check if the widget is a RawIdForeignKeyField #}
      if (rawIdWidgets[i].querySelector('.add-related') && rawIdWidgets[i].querySelector('.related-lookup')) {

        currentAddButton = rawIdWidgets[i].querySelector('.add-related')
        currentLookupButton = rawIdWidgets[i].querySelector('.related-lookup')

//      {# The hack, effectively we override the default behaviour and then run the click event for the #}
//      {# item lookup. From there, we wait until the iframe is instantiated for the lookup and them    #}
//      {# refresh the pop-up iframe with the url we want for adding a new file.                        #}
        currentAddButton.addEventListener('click', function (e) {
          e.preventDefault()
          currentLookupButton.click()
          var checkIframe = window.setInterval( function () {
            if (document.querySelector('.related-popup iframe')) {
              document.querySelector('iframe').src = '/admin/media/file/add/?_to_field=id&amp;_popup=1'
              window.clearInterval(checkIframe)
            }
          }, 10)
        })
      }
    }
  })
}) ();
