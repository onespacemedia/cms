from django.conf.urls import patterns, url

urlpatterns = patterns(
    "",
    url(r"^r/$", "django.contrib.contenttypes.views.shortcut", name="permalink_redirect"),
)
