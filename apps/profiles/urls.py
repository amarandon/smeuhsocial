from django.conf.urls import url
from . import views
from pinax.apps.autocomplete_app.views import username_autocomplete_friends


urlpatterns = [
    url(r"^username_autocomplete/$", username_autocomplete_friends,
        name="profile_username_autocomplete"),
    url(r"^$", views.profiles, name="profile_list"),
    url(r"^profile/(?P<username>[\w\._-]+)/$", views.profile,
        name="profile_detail"),
    url(r"^edit/$", views.profile_edit, name="profile_edit"),
]
