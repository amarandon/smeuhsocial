from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext_lazy as _

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from photologue.models import *

from friends.models import friend_set_for

from photos.models import Image, Pool
from photos.forms import PhotoUploadForm, PhotoEditForm

from tagging.models import TaggedItem


def group_and_bridge(request):
    """
    Given the request we can depend on the GroupMiddleware to provide the
    group and bridge.
    """
    
    # be group aware
    group = getattr(request, "group", None)
    if group:
        bridge = request.bridge
    else:
        bridge = None
    
    return group, bridge


def group_context(group, bridge):
    # @@@ use bridge
    ctx = {
        "group": group,
    }
    if group:
        ctx["group_base"] = bridge.group_base_template()
    return ctx


@login_required
def upload(request, form_class=PhotoUploadForm, template_name="photos/upload.html"):
    """
    upload form for photos
    """
    
    group, bridge = group_and_bridge(request)
    
    photo_form = form_class()
    if request.method == "POST":
        if request.POST.get("action") == "upload":
            photo_form = form_class(request.user, request.POST, request.FILES)
            if photo_form.is_valid():
                photo = photo_form.save(commit=False)
                photo.member = request.user
                photo.save(force_insert=True)

                # in group context we create a Pool object for it
                if group:
                    pool = Pool()
                    pool.photo = photo
                    group.associate(pool, gfk_field="content_object")
                    pool.save()
                
                messages.add_message(request, messages.SUCCESS,
                    ugettext("Successfully uploaded photo '%s'") % photo.title
                )
                
                include_kwargs = {"id": photo.id}
                if group:
                    redirect_to = bridge.reverse("photo_details", group, kwargs=include_kwargs)
                else:
                    redirect_to = reverse("photo_details", kwargs=include_kwargs)
                
                return HttpResponseRedirect(redirect_to)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "photo_form": photo_form,
    })
    
    return render(request, template_name, ctx)


@login_required
def your_photos(request, template_name="photos/yourphotos.html"):
    """
    photos for the currently authenticated user
    """
    
    group, bridge = group_and_bridge(request)
    
    photos = Image.objects.filter(member=request.user)
    
    if group:
        photos = group.content_objects(photos, join="pool", gfk_field="content_object")
    else:
        photos = photos.filter(pool__object_id=None)
    
    photos = photos.order_by("-date_added")
    
    ctx = group_context(group, bridge)
    ctx.update({
        "photos": photos,
    })
    
    return render(request, template_name, ctx)


@login_required
def photos(request, template_name="photos/latest.html"):
    """
    latest photos
    """
    
    group, bridge = group_and_bridge(request)
    
    photos = Image.objects.filter(
        Q(is_public=True) | Q(member=request.user)  | 
        Q(member__in=friend_set_for(request.user))
    )
    
    if group:
        photos = group.content_objects(photos, join="pool", gfk_field="content_object")
    else:
        photos = photos.filter(pool__object_id=None)
    
    photos = photos.order_by("-date_added")
    
    ctx = group_context(group, bridge)
    ctx.update({
        "photos": photos,
        "title": "Latest Photos"
    })
    
    return render(request, template_name, ctx)


@login_required
def most_viewed(request, template_name="photos/latest.html"):
    """
    latest photos
    """
    
    group, bridge = group_and_bridge(request)
    
    photos = Image.objects.filter(
        Q(is_public=True) | Q(member=request.user) 
        | Q(member__in=friend_set_for(request.user))
    )
    
    if group:
        photos = group.content_objects(photos, join="pool", gfk_field="content_object")
    else:
        photos = photos.filter(pool__object_id=None)
    
    photos = photos.order_by("-view_count")
    
    ctx = group_context(group, bridge)
    ctx.update({
        "photos": photos,
        "title": _("Most Viewed Photos")
    })
    
    return render(request, template_name, ctx)

def get_first_id_or_none(objects):
    try:
        return objects[0].id
    except IndexError:
        return None

def details(request, id, template_name="photos/details.html"):
    """
    show the photo details
    """
    photos = Image.objects.all()
    photos = photos.filter(pool__object_id=None)
    

    image_filter = Q(is_public=True)

    if request.user.is_authenticated():
        # allow owner and friend to see a private photo
        image_filter = image_filter | Q(member=request.user) | Q(member__in=friend_set_for(request.user))
        
    try:
        photo = photos.filter(image_filter, id=id)[0]
    except IndexError:                            
        raise Http404
        
    previous_photo_id = get_first_id_or_none(                                             
        photos.filter(image_filter, id__lt=photo.id).order_by('-id')
        )
    
    next_photo_id = get_first_id_or_none(
        photos.filter(image_filter, id__gt=photo.id).order_by('id')
        )         
    
            
    ctx = {
        "photo": photo,
        "photo_url": request.build_absolute_uri(photo.get_display_url()),
        "url": request.build_absolute_uri(),
        "is_me": photo.member == request.user,
        "previous_photo_id": previous_photo_id,
        "next_photo_id": next_photo_id,
    }
    
    return render(request, template_name, ctx)


@login_required
def user_photos(request, username, template_name="photos/user_photos.html"):
    """
    Get the photos of a user and display them
    """
        
    user = get_object_or_404(User, username=username)
    
    image_filter = Q(is_public=True)

    if request.user.is_authenticated():
        image_filter = image_filter | Q(member=request.user) | Q(member__in=friend_set_for(request.user))
    
    photos = Image.objects.filter(
        image_filter,
        member=user
        
    )           
    photos = photos.order_by("-date_added")
    group, bridge = group_and_bridge(request)
    ctx = group_context(group, bridge)
    ctx.update({
        "photos": photos,
        "username": username
    })    
    return render(request, template_name, ctx)

@login_required
def tagged_photos(request, tagname, template_name="photos/tagged_photos.html"):
    """
    Get the photos with a tag and display them
    """
        
    image_filter = Q(is_public=True)

    if request.user.is_authenticated():
        image_filter = image_filter | Q(member=request.user) | Q(member__in=friend_set_for(request.user))
        
    photos = TaggedItem.objects.get_by_model(Image, tagname).filter(image_filter).order_by("-date_added")   
    group, bridge = group_and_bridge(request)
    ctx = group_context(group, bridge)
    ctx.update({
        "photos": photos,
        "tag": tagname
    })    
    return render(request, template_name, ctx)


@login_required
def edit(request, id, form_class=PhotoEditForm, template_name="photos/edit.html"):
    
    group, bridge = group_and_bridge(request)
    
    photos = Image.objects.all()
    
    if group:
        photos = group.content_objects(photos, join="pool", gfk_field="content_object")
    else:
        photos = photos.filter(pool__object_id=None)
    
    photo = get_object_or_404(photos, id=id)
    photo_url = photo.get_display_url()
    
    if request.method == "POST":
        if photo.member != request.user:
            message.add_message(request, messages.ERROR,
                ugettext("You can't edit photos that aren't yours")
            )
            include_kwargs = {"id": photo.id}
            if group:
                redirect_to = bridge.reverse("photo_details", group, kwargs=include_kwargs)
            else:
                redirect_to = reverse("photo_details", kwargs=include_kwargs)
            
            return HttpResponseRedirect(reverse('photo_details', args=(photo.id,)))
        if request.POST["action"] == "update":
            photo_form = form_class(request.user, request.POST, instance=photo)
            if photo_form.is_valid():
                photoobj = photo_form.save(commit=False)
                photoobj.save()
                
                messages.add_message(request, messages.SUCCESS,
                    ugettext("Successfully updated photo '%s'") % photo.title
                )
                
                include_kwargs = {"id": photo.id}
                if group:
                    redirect_to = bridge.reverse("photo_details", group, kwargs=include_kwargs)
                else:
                    redirect_to = reverse("photo_details", kwargs=include_kwargs)
                
                return HttpResponseRedirect(redirect_to)
        else:
            photo_form = form_class(instance=photo)
    
    else:
        photo_form = form_class(instance=photo)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "photo_form": photo_form,
        "photo": photo,
        "photo_url": photo_url,
    })
    
    return render(request, template_name, ctx)

@login_required
def destroy(request, id):
    
    group, bridge = group_and_bridge(request)
    
    photos = Image.objects.all()
    
    if group:
        photos = group.content_objects(photos, join="pool", gfk_field="content_object")
    else:
        photos = photos.filter(pool__object_id=None)
    
    photo = get_object_or_404(photos, id=id)
    title = photo.title
    
    if group:
        redirect_to = bridge.reverse("photos_yours", group)
    else:
        redirect_to = reverse("photos_yours")
    
    if photo.member != request.user:
        message.add_message(request, messages.ERROR,
            ugettext("You can't edit photos that aren't yours")
        )
        return HttpResponseRedirect(redirect_to)
    
    if request.method == "POST" and request.POST["action"] == "delete":
        photo.delete()
        messages.add_message(request, messages.SUCCESS,
            ugettext("Successfully deleted photo '%s'") % title
        )
    
    return HttpResponseRedirect(redirect_to)

@login_required
def random(request):
    image_filter = Q(is_public=True)

    if request.user.is_authenticated():
        image_filter = image_filter | Q(member=request.user) | Q(member__in=friend_set_for(request.user))
        
    photo = Image.objects.filter(image_filter).order_by('?')[0]    
    return HttpResponseRedirect(reverse('photo_details', args=(photo.id,)))
