from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db.models import Q

from photos.models import Image

def get_first_id_or_none(objects):
    try:
        return objects[0].id
    except IndexError:
        return None

@login_required
def index(request):
    photo = Image.objects.filter(Q(is_public = True)).order_by('?')[0]    
    return HttpResponseRedirect(reverse('fukung_view', args=(photo.id,)))

@login_required
def view(request, photo_id):    
    photos = Image.objects.all()
    photos = photos.filter(pool__object_id=None)    
    photo = get_object_or_404(photos, Q(id=photo_id))
    previous_photo_id = get_first_id_or_none(
            photos.filter(id__lt=photo.id, is_public=True).order_by('-id'))
    next_photo_id = get_first_id_or_none(photos.filter(id__gt=photo.id,
        is_public=True).order_by('id'))
   
    return render(request, 'fukung/index.html',
        {'photo': photo, 
         'photo_url': photo.get_display_url(),
         'previous_photo_id' : previous_photo_id,
         'next_photo_id': next_photo_id
         })
