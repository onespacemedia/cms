Testing
=======

A very high test coverage is maintained in the project, typically at 99%+.  This helps us evaluate how the CMS works across various Python and Django versions.  As the CMS is not a Django project as such, you are unable to test it directly and instead have to create a CMS project and run the test from there.

Configuration
-------------

Install the Django version you would like to test against, then install the CMS with the test packages enabled and then create a new project::

    $ pip install Django==1.x.x
    $ pip install onespacemedia-cms[testing]
    $ start_cms_project.py testing . --without-people --without-faqs --without-jobs --skip-frontend

You can then run the tests with::

    $ ./manage.py test cms

If you would like coverage information you can use::

    $ coverage run --source=cms --omit='*migrations*' manage.py test cms && coverage html

This will output a set of HTML files which you can open with::

    $ open htmlcov/index.html
