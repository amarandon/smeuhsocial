import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from microblogging.models import Tweet, TweetInstance, Following, get_following_followers_lists
from microblogging.forms import TweetForm
from tagging.models import parse_tagged_text

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

@login_required
def personal(request, form_class=TweetForm,
        template_name="microblogging/personal.html", success_url=None):
    """
    just the tweets the current user is following
    """

    following_list, followers_list = get_following_followers_lists(request.user)

    if request.method == "POST":
        form = form_class(request.user, request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            tweet = form.save()
            if request.is_ajax():
                return HttpResponse("ok")
            else:
                if success_url is None:
                    success_url = reverse('microblogging.views.personal')
                return HttpResponseRedirect(success_url)
        reply = None
    else:
        reply = request.GET.get("reply", None)
        form = form_class()
        if reply:
            form.fields['text'].initial = u"@%s " % reply
        else:
            form.fields['text'].initial = u""
    tweets = TweetInstance.objects.tweets_for(request.user).order_by("-sent")
    return render(request, template_name, {
        "form": form,
        "reply": reply,
        "tweets": tweets,
        "following_list": following_list,
        "followers_list": followers_list
    })
personal = login_required(personal)

@login_required
def post_tweet(request, form_class=TweetForm, success_url=None):
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            tweet = form.save()
            parse_tagged_text(text, tweet.id, 'tweet')
            if request.is_ajax():
                return render(request, 'microblogging/_tweet.html', {
                    'tweet': tweet,
                    'prefix_sender': True ,
                    'extra_classes':  "fisrt odd",
                })
        else:
            data = json.dumps(dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()]))
            return HttpResponseBadRequest(data, content_type='application/json')
    if success_url is None:
        success_url = reverse('timeline.views.home')
    return HttpResponseRedirect(success_url)

@login_required
def public(request, template_name="microblogging/public.html"):
    """
    all the tweets
    """
    tweets = Tweet.objects.all().order_by("-sent")
    following_list, followers_list = get_following_followers_lists(request.user)

    return render(request, template_name, {
        "tweets": tweets,
        "following_list": following_list,
        "followers_list": followers_list
    })

@login_required
def single(request, id, template_name="microblogging/single.html"):
    """
    A single tweet.
    """
    tweet = get_object_or_404(Tweet, id=id)
    return render(request, template_name, {
        "tweet": tweet,
    })

@login_required
def toggle_follow(request, username):
    """
    Either follow or unfollow a user.
    """
    other_user = get_object_or_404(User, username=username)
    if request.user == other_user:
        is_me = True
    else:
        is_me = False
    if request.user.is_authenticated() and request.method == "POST" and not is_me:
        if request.POST["action"] == "follow":
            Following.objects.follow(request.user, other_user)
            messages.success(request, _("You are now following %(other_user)s") % {'other_user': other_user})
            if notification:
                notification.send([other_user], "tweet_follow", {"user": request.user})
        elif request.POST["action"] == "unfollow":
            Following.objects.unfollow(request.user, other_user)
            messages.success(request, _("You have stopped following %(other_user)s") % {'other_user': other_user})
    return HttpResponseRedirect(reverse("profile_detail", args=[other_user]))

