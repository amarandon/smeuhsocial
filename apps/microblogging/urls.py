from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.personal, name='tweets_you_follow'),
    url(r'^all/$', views.public, name='all_tweets'),
    url(r'^(\d+)/$', views.single, name='single_tweet'),
    url(r'^toggle_follow/(\w+)/$', views.toggle_follow,
        name='toggle_follow'),
    url(r'^post/$', views.post_tweet, name='post_tweet'),
]
