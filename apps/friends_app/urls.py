from django.conf.urls import url
from . import views


urlpatterns = [
    url(r"^$", views.friends, name="invitations"),
    url(r"^contacts/$", views.contacts,  name="invitations_contacts"),
    url(r"^accept/(\w+)/$", views.accept_join, name="friends_accept_join"),
    url(r"^invite/$", views.invite, name="invite_to_join"),
]
