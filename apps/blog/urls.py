from django.conf.urls import url

from blog import views
from blog.forms import BlogForm
from ajax_validation.views import validate


urlpatterns = [
    # all blog posts
    url(r"^blogs/?$", views.blogs,
        name="blog_list_all"),

    # blog post
    url(r"^(?P<username>[-\w]+)/blog/(?P<slug>[-\w]+)/source/?$",
        views.blog_post_source, name="blog_post_source"),
    url(r"^(?P<username>[-\w]+)/blog/(?P<slug>[-\w]+)/?$",
        views.post, name="blog_post"),

    # blog post for user
    url(r"^(?P<username>\w+)/blog/?$",
        views.user_blog_index, name="blog_list_user"),

    # your posts
    url(r"^blogs/your_posts/?$",
        views.your_posts, name="blog_list_yours"),

    # new blog post
    url(r"^blogs/new/$", views.new, name="blog_new"),

    # edit blog post
    url(r"^blogs/edit/(\d+)/$", views.edit, name="blog_edit"),

    # destory blog post
    url(r"^blogs/destroy/(\d+)/$",
        views.destroy, name="blog_destroy"),

    # ajax validation
    url(r"^blogs/validate/$", validate, {
        "form_class": BlogForm,
        "callback": lambda request, *args, **kwargs: {"user": request.user}
        }, name="blog_form_validate"),
]
