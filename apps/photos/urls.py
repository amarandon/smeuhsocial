from django.conf.urls import url
from . import views

urlpatterns = [
    # all photos or latest photos
    url(r"^$", views.photos, name="photos"),
    # most viewed photos
    url(r"^most_viewed/$", views.most_viewed, name="photo_most_viewed"),
    # a photos details
    url(r"^details/(?P<id>\d+)/$", views.details, name="photo_details"),
    # upload photos
    url(r"^upload/$", views.upload, name="photo_upload"),
    # your photos
    url(r"^yourphotos/$", views.your_photos, name="photos_yours"),
    # a members photos
    url(r"^user/(?P<username>[\w]+)/$", views.user_photos,
        name="photos_user"),
    # destroy photo
    url(r"^destroy/(?P<id>\d+)/$", views.destroy, name="photo_destroy"),
    # edit photo
    url(r"^edit/(?P<id>\d+)/$", views.edit, name="photo_edit"),
    # a random photo
    url(r"^random/$", views.random, name="photo_random"),
    # photos with a tag
    url(r"^tag/(?P<tagname>.+)/$", views.tagged_photos,
        name="photo_tag"),
]
