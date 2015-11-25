"""URLs used by the links application."""


from django.conf.urls import url


urlpatterns = [
    url(r"^$", "cms.apps.links.views.index", name="index")
]
