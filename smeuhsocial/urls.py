from django.conf import settings
from django.conf.urls import url, include
from django.views.generic import RedirectView
from django.contrib import admin
from django.conf.urls.static import static

from blog.feeds import BlogFeedAll, BlogFeedUser
from blog.models import Post
from friends_app.views import friends_objects
from microblogging.feeds import TweetFeedAll, TweetFeedUser
from microblogging.feeds import TweetFeedUserWithFriends
from microblogging.models import Tweet
from photos.models import Image
from smeuhoverride import feeds
from smeuhoverride.views import tag_index
from timeline.views import tag_home, user_home, home, legacy

admin.autodiscover()


handler500 = "pinax.views.server_error"


tweets_feed_dict = {"feed_dict": {
    "all": TweetFeedAll,
    "only": TweetFeedUser,
    "with_friends": TweetFeedUserWithFriends,
}}

blogs_feed_dict = {"feed_dict": {
    "all": BlogFeedAll,
    "only": BlogFeedUser,
}}

urlpatterns = [
    url(r"^favicon.ico/?$", RedirectView.as_view(
        url=settings.STATIC_URL + 'img/favicon.ico',
        permanent=True)),
    url(r"^$", home, name="home"),
    url(r"5c/$", legacy, name="legacy"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("account.urls")),
    url(r"^profiles/", include("profiles.urls")),

    # Blog URLs ############################################

    url(r"^(?P<username>[\w\._-]+)/blog/feed/?$", feeds.UserBlogPosts(),
        name="user_blog_feed"),
    url(r"^", include("blog.urls")),


    # /END Blog URLs #######################################

    url(r"^invitations/", include("friends_app.urls")),
    url(r"^notices/", include("notification.urls")),
    url(r"^messages/", include("messages.urls")),
    url(r"^touites/", include("microblogging.urls")),
    url(r"^comments/", include("threadedcomments.urls")),
    url(r"^i18n/", include("django.conf.urls.i18n")),
    url(r"^photos/", include("photos.urls")),
    url(r"^avatar/", include("avatar.urls")),
    url(r"^fu/",  include("fukung.urls")),
    url(r"^timeline/", include("timeline.urls")),
    url(r"^artist/", include("artist.urls")),

    # Feeds urls
    url(r"^feeds/touites/(?P<username>[\w\._-]+)/with_friends/?$",
        feeds.UserTweetWithFriends(
        ), name="user_friends_tweets"),
    url(r"^feeds/touites/(?P<username>[\w\._-]+)/?$", feeds.UserTweet(),
        name="user_tweets"),
    url(r"^feeds/touites/?$",
        feeds.AllTweet(), name="all_tweets_feed"),
    url(r"^feeds/photos/?$",
        feeds.AllPhotos(), name="all_photos_feed"),
    url(r"^feeds/comments/?$",
        feeds.AllComments(), name="all_comments_feed"),
    url(r"^feeds/blogs/?$", feeds.AllBlogPosts(),
        name="all_blogs_feed"),
]

# @@@ for now, we'll use friends_app to glue this stuff together

friends_photos_kwargs = {
    "template_name": "photos/friends_photos.html",
    "friends_objects_function": lambda users: Image.objects.filter(member__in=users).order_by("-date_added"),
}

friends_blogs_kwargs = {
    "template_name": "blog/friends_posts.html",
    "friends_objects_function": lambda users: Post.objects.filter(author__in=users),
}

friends_tweets_kwargs = {
    "template_name": "microblogging/friends_tweets.html",
    "friends_objects_function": lambda users: Tweet.objects.filter(sender_id__in=[user.id for user in users], sender_type__name="user"),
}


urlpatterns += [
    url(r"^photos/friends_photos/$", friends_objects,
        kwargs=friends_photos_kwargs, name="friends_photos"),
    url(r"^blog/friends_blogs/$", friends_objects,
        kwargs=friends_blogs_kwargs, name="friends_blogs"),
    url(r"^touites/friends_tweets/$", friends_objects,
        kwargs=friends_tweets_kwargs, name="friends_tweets"),
    url(r"^tags/(?P<tagname>.+)/$", tag_home, name="tag_homepage"),
    url(r"^tags/$", tag_index, kwargs={'limit': 1000},
        name="tagging_ext_index"),
    url("^(?P<username>[\w\._-]+)/music/", include(
        "audiotracks.urls"), name="user_track"),
    url("^music/", include("audiotracks.urls")),
    url(r"^(?P<username>[\w\._-]+)/$", user_home, name="profile_detail"),
]

if settings.SERVE_MEDIA:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
