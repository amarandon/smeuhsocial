from django.conf.urls import url
from . import views


urlpatterns = [
    # all items
    url(r"^$", views.index, name="fukung"),
    url(r"^v/(?P<photo_id>\d+)/$", views.view, name="fukung_view"),
]
