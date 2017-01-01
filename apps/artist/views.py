from django.shortcuts import render
from django.template import RequestContext
from django.db.models import Count

from audiotracks.models import get_track_model


def index(request):
    
    names = get_track_model().objects.values('artist').annotate(total=Count('artist')).distinct().order_by('artist')
    
    ncols = 3
    
    columns = []
    
    count = names.count()
    
    csize = count / ncols
    
    remains = count % ncols
    
    current = 0
    
    for _ in range(ncols):
        if current > count:
            break
        end = current + csize
        if remains:
            end += 1
            remains -= 1
            
        if end > count:
            end = count
        
        columns.append(names[current:end])
        current = end   
    
    
    return render(request, "artist/index.html", { 'artists': names, 'columns': columns })

def artist(request, name):
    
    tracks = get_track_model().objects.filter(artist = name).order_by('-created_at')
    
    return render(request, "artist/artist.html", {'tracks': tracks, 'artist': name })
