from django.conf.urls import patterns, url


urlpatterns = patterns(
    "",
    url("^$", lambda: None, name="index"),
    url("^(?P<url_title>[^/]+)/$", lambda: None, name="detail"),
)
