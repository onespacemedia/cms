"""URLs used by the links application."""


from django.conf.urls import url


urlpatterns = [
    url(r"^$", "index", name="index")
]
