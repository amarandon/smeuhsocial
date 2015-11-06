"""

views for the mysmeuh timeline application.

this module grows and gets bloated ... needs a serious refactoring soon, with 
an abstraction over pages with meta things over timeline, photos, tracks and 
blogs is strongly needed.
"""
import datetime
from django.db.models import Q

from django.views.generic import TemplateView  # , RedirectView
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect

# model import
from microblogging.models import Tweet
from photos.models import Image
from audiotracks.models import get_track_model
Track = get_track_model()
from blog.models import Post
from threadedcomments.models import ThreadedComment
from friends.models import friend_set_for
from microblogging.models import get_following_followers_lists
from friends.forms import InviteFriendForm
from friends.models import FriendshipInvitation, Friendship
from microblogging.models import Following
from tagging.models import TaggedItem, Tag
from timeline.models import TimeLineItem

class TimeLineView(TemplateView):

    template_name = "timeline/index.html"

    def get_context_data(self, **kwargs):
        context = super(TimeLineView, self).get_context_data(**kwargs)
        # TODO use a query parameter for the time delta. here is 3 months
        ago = datetime.datetime.now() - datetime.timedelta(30)

        tweets = [
            TimeLineItem(item, item.sent, item.sender, "timeline/_tweet.html")
            for item in Tweet.objects.all().filter(sent__gte=ago).order_by("-sent")
            ]

        posts = [
            TimeLineItem(item, item.updated_at, item.author, "timeline/_post.html")
            for item in Post.objects.all().filter(publish__gte=ago, status=2).order_by("-publish")
            ]

        image_filter = Q(is_public=True)

        if self.request.user.is_authenticated():
            image_filter = image_filter | Q(member=self.request.user) | Q(member__in=friend_set_for(self.request.user))
        
        images = [
            TimeLineItem(item, item.date_added, item.member, "timeline/_photo.html")
            for item in Image.objects.all().filter(image_filter).filter(date_added__gte=ago).order_by("-date_added")
            ]        

        tracks = [
            TimeLineItem(item, item.updated_at, item.user, "timeline/_track.html")
            for item in Track.objects.all().filter(created_at__gte=ago).order_by("-created_at")
            ]

        comments = [
            TimeLineItem(item, item.date_submitted, item.user, "timeline/_comment.html")
            for item in ThreadedComment.objects.all().filter(date_submitted__gte=ago).order_by("-date_submitted")
            ]

        items = merge(tweets, images, posts, tracks, comments, field="date")
        for index, item in enumerate(items):
            item.index = index

        context['timelineitems'] = group_comments(items)
        context['posts'] = posts
        context['prefix_sender'] = True
        return context

def merge_lists(left, right, field=None):
    i, j = 0, 0
    result = []
    while (i < len(left) and j < len(right)):
        if getattr(left[i], field) >= getattr(right[j], field):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def merge(*querysets, **kwargs):
    field = kwargs.get('field')
    if field is None:
        raise TypeError('you need to provide a key to do comparisons on')
    if len(querysets) == 1:
        return querysets[0]

    qs = [list(x) for x in querysets]
    q1, q2 = qs.pop(), qs.pop()
    result = merge_lists(q1, q2, field)
    for q in qs:
        result = merge_lists(result, q, field)
    return result

def group_comments(items):
    grouped = []            
    for tlitem in items:
        item = tlitem.item
        if isinstance(item, ThreadedComment):
            key = (item.content_type_id, item.object_id)
            if grouped: 
                prev = grouped[-1]
                if isinstance(prev.item, ThreadedComment) and key == (prev.item.content_type_id, prev.item.object_id):
                    if hasattr(prev, "comments"):
                        prev.comments.append(tlitem)
                    else:
                        prev = grouped.pop()
                        group_item = TimeLineItem(item, item.date_submitted, item.user, "timeline/_comment_group.html")
                        group_item.firstcomment = prev.item
                        group_item.comments = [ prev, group_item ]                    
                        grouped.append(group_item)
                else:
                    grouped.append(tlitem)                
            else:
                grouped.append(tlitem)            
        else:
            grouped.append(tlitem)
    return grouped
            
        
class HomePageView(TimeLineView):

    template_name = "timeline/homepage/homepage.html"

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        # reduce the timeline items
        context['timelineitems'] = group_comments(context['timelineitems'][:16])
        image_filter = Q(is_public=True)

        if self.request.user.is_authenticated():
            image_filter = image_filter | Q(member=self.request.user) | Q(member__in=friend_set_for(self.request.user))
        context['latest_photos'] = Image.objects.all().filter(image_filter).order_by("-date_added")[:16]
        context['latest_blogs'] = Post.objects.all().filter(status=2).order_by("-publish")[:10]
        context['latest_tracks'] = Track.objects.all().order_by("-created_at")[:6]
        return context

class FriendsPageView(TemplateView):

    template_name = "timeline/friends.html"

    def get_context_data(self, **kwargs):
        context = super(FriendsPageView, self).get_context_data(**kwargs)
        # TODO use a query parameter for the time delta. here is 3 months
        ago = datetime.datetime.now() - datetime.timedelta(30)
        friends = friend_set_for(self.request.user)

        tweets = [
            TimeLineItem(item, item.sent, item.sender, "timeline/_tweet.html")
            for item in Tweet.objects.all().filter(sent__gte=ago, sender_id__in=[user.id for user in friends], sender_type__model="user").order_by("-sent")
            ]

        posts = [
            TimeLineItem(item, item.publish, item.author, "timeline/_post.html")
            for item in Post.objects.all().filter(publish__gte=ago, status=2, author__in=friends).order_by("-publish")
            ]

        images = [
            TimeLineItem(item, item.date_added, item.member, "timeline/_photo.html")
            for item in Image.objects.all().filter(Q(is_public=True) | Q(member__in=friend_set_for(self.request.user))).filter(date_added__gte=ago, member__in=friends).order_by("-date_added")
            ]

        tracks = [
            TimeLineItem(item, item.updated_at, item.user, "timeline/_track.html")
            for item in Track.objects.all().filter(created_at__gte=ago, user__in=friends).order_by("-created_at")
            ]

        comments = [
            TimeLineItem(item, item.date_submitted, item.user, "timeline/_comment.html")
            for item in ThreadedComment.objects.all().filter(date_submitted__gte=ago, user__in=friends).order_by("-date_submitted")
            ]

        items = merge(tweets, images, posts, tracks, comments, field="date")
        for index, item in enumerate(items):
            item.index = index + 1

        context['timelineitems'] = group_comments(items)
        context['prefix_sender'] = True
        return context

class FollowingPageView(TemplateView):

    template_name = "timeline/following.html"

    def get_context_data(self, **kwargs):
        context = super(FollowingPageView, self).get_context_data(**kwargs)
        # TODO use a query parameter for the time delta. here is 3 months
        ago = datetime.datetime.now() - datetime.timedelta(30)
        following_list, followers_list = get_following_followers_lists(self.request.user)

        tweets = [
            TimeLineItem(item, item.sent, item.sender, "timeline/_tweet.html")
            for item in Tweet.objects.all().filter(sent__gte=ago, sender_id__in=[user.id for user in following_list], sender_type__model="user").order_by("-sent")
            ]

        posts = [
            TimeLineItem(item, item.updated_at, item.author, "timeline/_post.html")
            for item in Post.objects.all().filter(publish__gte=ago, status=2, author__in=following_list).order_by("-publish")
            ]

        images = [
            TimeLineItem(item, item.date_added, item.member, "timeline/_photo.html")
            for item in Image.objects.all().filter(Q(is_public=True) | Q(member__in=friend_set_for(self.request.user))).filter(date_added__gte=ago, member__in=following_list).order_by("-date_added")
            ]

        tracks = [
            TimeLineItem(item, item.updated_at, item.user, "timeline/_track.html")
            for item in Track.objects.all().filter(created_at__gte=ago, user__in=following_list).order_by("-created_at")
            ]

        comments = [
            TimeLineItem(item, item.date_submitted, item.user, "timeline/_comment.html")
            for item in ThreadedComment.objects.all().filter(date_submitted__gte=ago, user__in=following_list).order_by("-date_submitted")
            ]

        items = merge(tweets, images, posts, tracks, comments, field="date")
        for index, item in enumerate(items):
            item.index = index + 1
        context['timelineitems'] = group_comments(items)
        context['prefix_sender'] = True
        return context

class UserPageView(TemplateView):
    
    template_name = "timeline/user.html"
    
    def get_context_data(self, **kwargs):
        context = super(UserPageView, self).get_context_data(**kwargs)
        name = context.get('username', None)
        limit = 64
        if name:
            user = other_user = get_object_or_404(User, username=name)
        else:
            user = other_user = self.request.user
        
        if self.request.user == other_user:
            context['is_me'] = True
            context['is_friend'] = False
        elif self.request.user.is_authenticated():
            context['is_friend'] = Friendship.objects.are_friends(self.request.user, other_user)
            context['is_following'] = Following.objects.is_following(self.request.user, other_user)
        context['other_friends'] = Friendship.objects.friends_for_user(other_user)
        context['other_user'] = other_user
        
        tweets = [
            TimeLineItem(item, item.sent, item.sender, "timeline/_tweet.html")
            for item in Tweet.objects.all().filter(sender_id=user.id, sender_type__model="user").order_by("-sent")[:limit]
            ]

        context['latest_blogs'] = Post.objects.all().filter(status=2, author=user).order_by("-publish")[:limit]

        posts = [
            TimeLineItem(item, item.updated_at, item.author, "timeline/_post.html")
            for item in context['latest_blogs']
            ]

        image_filter = Q(is_public=True, member=user)

        if self.request.user.is_authenticated():
            image_filter = image_filter | Q(member=user, member__in=friend_set_for(self.request.user))

        context['latest_photos'] = Image.objects.all().filter(image_filter).order_by("-date_added")[:limit]

        images = [
            TimeLineItem(item, item.date_added, item.member, "timeline/_photo.html")
            for item in context['latest_photos']
            ]

        context['latest_tracks'] = Track.objects.all().filter(user=user).order_by("-created_at")[:limit]

        tracks = [
            TimeLineItem(item, item.updated_at, item.user, "timeline/_track.html")
            for item in context['latest_tracks']
            ]

        comments = [
            TimeLineItem(item, item.date_submitted, item.user, "timeline/_comment.html")
            for item in ThreadedComment.objects.all().filter(user=user).order_by("-date_submitted")[:limit]
            ]
        
        items = merge(tweets, images, posts, tracks, comments, field="date")
        for index, item in enumerate(items):
            item.index = index + 1
        context['timelineitems'] = group_comments(items)[:limit]
        context['prefix_sender'] = True        
        return context
    

class UserHomePageView(TemplateView):

    template_name = "timeline/homepage/user.html"

    def get_context_data(self, **kwargs):
        context = super(UserHomePageView, self).get_context_data(**kwargs)
        
        other_friends = None
        username = name = context.get('username', None)

        if name:
            user = other_user = get_object_or_404(User, username=name)
        else:
            user = other_user = self.request.user

        if self.request.user == other_user:
            context['is_me'] = True
            is_friend = False
        elif self.request.user.is_authenticated():
            is_friend = context['is_friend'] = Friendship.objects.are_friends(self.request.user, other_user)
            context['is_following'] = Following.objects.is_following(self.request.user, other_user)
        else:
            is_friend = False
        context['other_friends'] = Friendship.objects.friends_for_user(other_user)

        context['other_user'] = other_user
        tweets = [
            TimeLineItem(item, item.sent, item.sender, "timeline/_tweet.html")
            for item in Tweet.objects.all().filter(sender_id=user.id, sender_type__model="user").order_by("-sent")[:32]
            ]

        context['latest_blogs'] = Post.objects.all().filter(status=2, author=user).order_by("-publish")[:32]

        posts = [
            TimeLineItem(item, item.updated_at, item.author, "timeline/_post.html")
            for item in context['latest_blogs']
            ]

        image_filter = Q(is_public=True, member=user)

        if self.request.user.is_authenticated():
            image_filter = image_filter | Q(member=user, member__in=friend_set_for(self.request.user))

        context['latest_photos'] = Image.objects.all().filter(image_filter).order_by("-date_added")[:32]

        images = [
            TimeLineItem(item, item.date_added, item.member, "timeline/_photo.html")
            for item in context['latest_photos']
            ]

        context['latest_tracks'] = Track.objects.all().filter(user=user).order_by("-created_at")[:32]

        tracks = [
            TimeLineItem(item, item.updated_at, item.user, "timeline/_track.html")
            for item in context['latest_tracks']
            ]

        comments = [
            TimeLineItem(item, item.date_submitted, item.user, "timeline/_comment.html")
            for item in ThreadedComment.objects.all().filter(user=user).order_by("-date_submitted")[:32]
            ]
        
        items = merge(tweets, images, posts, tracks, comments, field="date")[:16]
        for index, item in enumerate(items):
            item.index = index + 1
        context['timelineitems'] = group_comments(items)
        context['prefix_sender'] = True


        invite_form = None
        if is_friend:
            previous_invitations_to = None
            previous_invitations_from = None
            if self.request.method == "POST":
                if self.request.POST.get("action") == "remove":  # @@@ perhaps the form should just post to friends and be redirected here
                    Friendship.objects.remove(self.request.user, other_user)
                    messages.add_message(self.request, messages.SUCCESS,
                        ugettext("You have removed %(from_user)s from friends") % {
                            "from_user": other_user
                        }
                    )
                    is_friend = False
                    invite_form = InviteFriendForm(self.request.user, {
                        "to_user": username,
                        "message": ugettext("Let's be friends!"),
                    })

        else:
            if self.request.user.is_authenticated() and self.request.method == "POST":
                pass
            else:
                invite_form = InviteFriendForm(self.request.user, {
                    "to_user": username,
                    "message": ugettext("Let's be friends!"),
                })
                previous_invitations_to = None
                previous_invitations_from = None

        context['invite_form'] = invite_form
        context['previous_invitations_to'] = previous_invitations_to
        context['previous_invitations_from'] = previous_invitations_from
        context['other_friends'] = other_friends
        return context


    def post(self, *args, **kw):
        if self.request.POST.get("action") == "invite":
            username = self.request.POST.get("to_user")
            other_user = get_object_or_404(User, username=username)

            invite_form = InviteFriendForm(self.request.user, self.request.POST)
            if invite_form.is_valid():
                invite_form.save()
                messages.success(self.request, _("Friendship requested with %(username)s") % {
                    'username': invite_form.cleaned_data['to_user']
                })
        elif self.request.POST.get("action") == "remove":
            username = kw['username']
            other_user = get_object_or_404(User, username=username)
            Friendship.objects.remove(self.request.user, other_user)
            messages.add_message(self.request, messages.SUCCESS,
                ugettext("You have removed %(from_user)s from friends") % {
                    "from_user": other_user
                }
            )
        else:
            username = kw['username']
            other_user = get_object_or_404(User, username=username)
            invite_form = InviteFriendForm(self.request.user, {
                "to_user": username,
                "message": ugettext("Let's be friends!"),
            })
            invitation_id = self.request.POST.get("invitation", None)
            if self.request.POST.get("action") == "accept":
                try:
                    invitation = FriendshipInvitation.objects.get(id=invitation_id)
                    if invitation.to_user == self.equest.user:
                        invitation.accept()
                        messages.add_message(self.request, messages.SUCCESS,
                            ugettext("You have accepted the friendship request from %(from_user)s") % {
                                "from_user": invitation.from_user
                            }
                        )
                except FriendshipInvitation.DoesNotExist:
                    pass
            elif self.request.POST.get("action") == "decline":
                try:
                    invitation = FriendshipInvitation.objects.get(id=invitation_id)
                    if invitation.to_user == self.request.user:
                        invitation.decline()
                        messages.add_message(self.request, messages.SUCCESS,
                            ugettext("You have declined the friendship request from %(from_user)s") % {
                                "from_user": invitation.from_user
                            }
                        )
                except FriendshipInvitation.DoesNotExist:
                    pass

        return HttpResponseRedirect(reverse("timeline.views.user_home", kwargs={"username": username}))

class TagPageView(TemplateView):

    template_name = "timeline/tag.html"
    
    def get_context_data(self, **kwargs):
        context = super(TagPageView, self).get_context_data(**kwargs)
        tag_instance = get_object_or_404(Tag, name__iexact=context.get("tagname"))                       
        
        context['tag'] = tag = tag_instance.name
        
        # ago = datetime.datetime.now() - datetime.timedelta(30)
        
        # limit = 64
        
        tweets = [
            TimeLineItem(item, item.sent, item.sender, "timeline/_tweet.html")
            for item in TaggedItem.objects.get_by_model(Tweet, tag).order_by("-sent")  # [:limit]
            ]

        context['latest_blogs'] = TaggedItem.objects.get_by_model(Post, tag).filter(status=2).order_by("-publish")  # [:limit]

        posts = [
            TimeLineItem(item, item.updated_at, item.author, "timeline/_post.html")
            for item in context['latest_blogs']
            ]

        image_filter = Q(is_public=True)

        if self.request.user.is_authenticated():
            image_filter = image_filter | Q(member=self.request.user) | Q(member__in=friend_set_for(self.request.user))

        context['latest_photos'] = TaggedItem.objects.get_by_model(Image, tag).filter(image_filter).order_by("-date_added")  # [:limit]

        images = [
            TimeLineItem(item, item.date_added, item.member, "timeline/_photo.html")
            for item in context['latest_photos']
            ]

        context['latest_tracks'] = TaggedItem.objects.get_by_model(Track, tag).order_by("-created_at")        

        tracks = [
            TimeLineItem(item, item.created_at, item.user, "timeline/_track.html")
            for item in context['latest_tracks']
            ]

        comments = [
            TimeLineItem(item, item.date_submitted, item.user, "timeline/_comment.html")
            for item in TaggedItem.objects.get_by_model(ThreadedComment, tag).order_by("-date_submitted")
            ]
        
        # no tag for comment yet. so : no comment :)
        
        # Tag.objects.get_for_object(self.obj.resolve(context))
        
        
        items = merge(tweets, images, posts, tracks, comments, field="date")
        for index, item in enumerate(items):
            item.index = index + 1
        context['timelineitems'] = group_comments(items) 
        context['prefix_sender'] = True
        return context
    

class TagHomePageView(TemplateView):

    template_name = "timeline/homepage/tag.html"

    def get_context_data(self, **kwargs):
        context = super(TagHomePageView, self).get_context_data(**kwargs)
        tag_instance = get_object_or_404(Tag, name__iexact=context.get("tagname"))                       
        
        context['tag'] = tag = tag_instance.name
        
        # ago = datetime.datetime.now() - datetime.timedelta(30)
                
        tweets = [
            TimeLineItem(item, item.sent, item.sender, "timeline/_tweet.html")
            for item in TaggedItem.objects.get_by_model(Tweet, tag).order_by("-sent")[:16]
            ]

        context['latest_blogs'] = TaggedItem.objects.get_by_model(Post, tag).filter(status=2).order_by("-publish")[:10]

        posts = [
            TimeLineItem(item, item.publish, item.author, "timeline/_post.html")
            for item in context['latest_blogs']
            ]

        image_filter = Q(is_public=True)

        if self.request.user.is_authenticated():
            image_filter = image_filter | Q(member=self.request.user) | Q(member__in=friend_set_for(self.request.user))

        context['latest_photos'] = TaggedItem.objects.get_by_model(Image, tag).filter(image_filter).order_by("-date_added")[:16]

        images = [
            TimeLineItem(item, item.date_added, item.member, "timeline/_photo.html")
            for item in context['latest_photos']
            ]

        context['latest_tracks'] = TaggedItem.objects.get_by_model(Track, tag).order_by("-created_at")        

        tracks = [
            TimeLineItem(item, item.updated_at, item.user, "timeline/_track.html")
            for item in context['latest_tracks']
            ]

        comments = [
            TimeLineItem(item, item.date_submitted, item.user, "timeline/_comment.html")
            for item in TaggedItem.objects.get_by_model(ThreadedComment, tag).order_by("-date_submitted")
            ]
        
        # no tag for comment yet. so : no comment :)
        
        # Tag.objects.get_for_object(self.obj.resolve(context))
        
        
        items = merge(tweets, images, posts, tracks, comments, field="date")[:16]
        for index, item in enumerate(items):
            item.index = index + 1
        context['timelineitems'] = group_comments(items) 
        context['prefix_sender'] = True
        return context
 

# old stuff extracted from the main urls.py file, to run the 5 column home page
class LegacyHomePageView(TemplateView):

    template_name = "timeline/homepage/legacy.html"

    def get_context_data(self, **kwargs):
        context = super(LegacyHomePageView, self).get_context_data(**kwargs)
        context['latest_tweets'] = lambda: Tweet.objects.all().order_by(
            "-sent")[:12]
        context['latest_blogs'] = lambda: Post.objects.filter(
            status=2).order_by("-publish")[:10]
            
        image_filter = Q(is_public=True)

        if self.request.user.is_authenticated():
            image_filter = image_filter | Q(member=self.request.user) | Q(member__in=friend_set_for(self.request.user))
            
        context['latest_photos'] = lambda: Image.objects.all().filter(image_filter).order_by(
            "-date_added")[:18]
        context['latest_tracks'] = lambda: Track.objects.all().order_by(
            "-created_at")[:6]
        context['prefix_sender'] = True
        return context

timeline = TimeLineView.as_view()

home = HomePageView.as_view()

legacy = LegacyHomePageView.as_view()

friends = login_required(FriendsPageView.as_view())

following = login_required(FollowingPageView.as_view())

user_timeline = UserPageView.as_view()

user_home = UserHomePageView.as_view()

tag_timeline = TagPageView.as_view()

tag_home = TagHomePageView.as_view()
