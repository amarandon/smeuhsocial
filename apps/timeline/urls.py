from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^$", views.timeline, name="timeline"),
    url(r"^homepage$", views.home, name="timeline_homepage"),
    url(r"^legacy$", views.legacy, name="5c_homepage"),
    url(r"^friends$", views.friends, name="friends_news"),
    url(r"^following$", views.following, name="following_news"),
    url(r"^user/home/(?P<username>[\w\._-]+)/$", views.user_home,
        name="user_homepage"),
    url(r"^user/(?P<username>[\w\._-]+)/$",
        views.user_timeline, name="user_timeline"),
    url(r"^tag/home/(?P<tagname>.+)/$", views.tag_home,
        name="tag_homepage"),
    url(r"^tag/(?P<tagname>.+)/$", views.tag_timeline,
        name="tag_timeline"),
]
