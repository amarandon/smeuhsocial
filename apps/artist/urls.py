from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^$", views.index, name="artist_index"),
    url(r"^(?P<name>.+)/$", views.artist, name="artist_tracks"),
]
