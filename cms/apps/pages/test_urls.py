from django.conf.urls import patterns, url


def view():
    pass

urlpatterns = patterns(
    "",
    url("^$", view, name="index"),
    url("^(?P<url_title>[^/]+)/$", view, name="detail"),
)
