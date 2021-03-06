from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from blog.models import Post, PUBLISHED, DRAFT
from blog.forms import BlogForm

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None
try:
    from friends.models import Friendship
    friendship_support = True
except ImportError:
    friendship_support = False


def blogs(request, username=None, template_name="blog/blogs.html"):
    blogs = Post.objects.filter(
        status=PUBLISHED
    ).select_related('author').order_by("-publish")
    if username is not None:
        user = get_object_or_404(User, username=username.lower())
        blogs = blogs.filter(author=user)
    return render(request, template_name, {"blogs": blogs})


def post(request, username, slug,
         template_name="blog/post.html"):
    post = Post.objects.filter(
        slug=slug,
        author__username=username
    )
    if not post:
        raise Http404

    if post[0].status == DRAFT and post[0].author != request.user:
        raise Http404

    return render(request, template_name, {
        "post": post[0],
        "url": request.build_absolute_uri(post[0].get_absolute_url()),
    })


@login_required
def your_posts(request, template_name="blog/your_posts.html"):
    return render(request, template_name, {
        "blogs": Post.objects.filter(author=request.user),
    })


@login_required
def destroy(request, id):
    post = Post.objects.get(pk=id)
    title = post.title
    if post.author != request.user:
        messages.add_message(
            request, messages.ERROR,
            _("You can't delete posts that aren't yours"))
        return HttpResponseRedirect(reverse("blog_list_yours"))

    if request.method == "POST" and request.POST["action"] == "delete":
        post.delete()
        messages.add_message(
            request, messages.SUCCESS,
            _("Successfully deleted post '%s'") % title)
        return HttpResponseRedirect(reverse("blog_list_yours"))
    else:
        return HttpResponseRedirect(reverse("blog_list_yours"))


@login_required
def new(request, form_class=BlogForm, template_name="blog/new.html"):
    if request.method == "POST":
        if request.POST["action"] == "create":
            blog_form = form_class(request.user, request.POST)
            if blog_form.is_valid():
                blog = blog_form.save(commit=False)
                blog.author = request.user
                if getattr(settings, 'BEHIND_PROXY', False):
                    blog.creator_ip = request.META["HTTP_X_FORWARDED_FOR"]
                else:
                    blog.creator_ip = request.META['REMOTE_ADDR']
                blog.save()
                # @@@ should message be different if published?
                messages.add_message(
                    request, messages.SUCCESS,
                    _("Successfully saved post '%s'") % blog.title)
                if notification:
                    if blog.status == PUBLISHED:
                        if friendship_support:
                            send_notifications(blog)
                return HttpResponseRedirect(reverse("blog_list_yours"))
        else:
            blog_form = form_class()
    else:
        blog_form = form_class()

    return render(request, template_name, {
        "blog_form": blog_form
    })


def send_notifications(blog):
    friends = Friendship.objects.friends_for_user(blog.author)
    recipients = (x['friend'] for x in friends)
    notification.send(recipients, "blog_friend_post", {"post": blog})


@login_required
def edit(request, id, form_class=BlogForm, template_name="blog/edit.html"):
    post = get_object_or_404(Post, id=id)

    if request.method == "POST":
        if post.author != request.user:
            messages.add_message(
                request, messages.ERROR,
                _("You can't edit posts that aren't yours"))
            return HttpResponseRedirect(reverse("blog_list_yours"))
        if request.POST["action"] == "update":
            blog_form = form_class(request.user, request.POST, instance=post)
            if blog_form.is_valid():
                blog = blog_form.save(commit=False)
                blog.save()
                messages.add_message(
                    request, messages.SUCCESS,
                    _("Successfully updated post '%s'") % blog.title)
                return HttpResponseRedirect(reverse("blog_list_yours"))
        else:
            blog_form = form_class(instance=post)
    else:
        blog_form = form_class(instance=post)

    return render(request, template_name, {
        "blog_form": blog_form,
        "post": post,
    })


def user_blog_index(request, username, template_name="blog/user_blog.html"):
    blogs = Post.objects.filter(
        status=PUBLISHED
    ).select_related().order_by("-publish")
    if username is not None:
        user = get_object_or_404(User, username=username.lower())
        blogs = blogs.filter(author=user)
    return render(request, template_name, {
        "blogs": blogs,
        "username": username,
    })


def blog_post_source(request, username, slug):
    post = get_object_or_404(Post, slug=slug, author__username=username)

    if post.status == DRAFT and post.author != request.user:
        raise Http404

    return HttpResponse(post.body, content_type="text/plain; charset=utf-8")
