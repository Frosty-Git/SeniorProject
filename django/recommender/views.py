from recommender.forms import SearchForm
from django.shortcuts import render
from django.http import Http404
from .models import *
from .forms import *
from django.views.decorators.http import require_POST, require_GET
import numpy as np
from recommender.Scripts.search import search_albums, search_artists, search_tracks

#----Dr Baliga's Code----

def find_albums(artist, from_year = None, to_year = None):
    query = Musicdata.objects.filter(artists__contains = artist)
    if from_year is not None:
        query = query.filter(year__gte = from_year)
    if to_year is not None:
        query = query.filter(year__lte = to_year)
    return list(query.order_by('-popularity').values('id','name','year'))
    

@require_POST
def searchform_post(request):
    # create a form instance and populate it with data from the request:
    form = SearchForm(request.POST)
    # check whether it's valid:
    if form.is_valid():
        # process the data in form.cleaned_data as required
        from_year = None if form.cleaned_data['from_year'] == None else int(form.cleaned_data['from_year'])
        to_year = None if form.cleaned_data['to_year'] == None else int(form.cleaned_data['to_year'])
        albums = find_albums(
                form.cleaned_data['artist'],
                from_year,
                to_year
            )
            
        # Random 3 of top 10 popular albums
        albums = list(np.random.permutation(albums[:10]))[:3] 
        return render(request, 'recommender/searchform.html', {'form': form, 'albums': albums })
    else:
        raise Http404('Something went wrong')


@require_GET
def searchform_get(request):
    form = SearchForm()
    return render(request, 'recommender/searchform.html', {'form': form})


#----End Dr Baliga's Code----

# Home Page
def home(request):
    ourSearchForm = OurSearchForm()

    context={
        'name': 'Pengbeats',
        'ourSearchForm': ourSearchForm,
    }
    return render(request, 'home.html', context)

# Search Results Page
def results(request):

    if request.method == "POST":
        form = OurSearchForm(request.POST)
        if form.is_valid():
            term = request.POST.get('term')
            track_ids = search_tracks(term)
            album_ids = search_albums(term)
            artist_ids = search_artists(term)
            context = {
                'term' : term,
                'tracks' : track_ids,
                'albums' : album_ids,
                'artists' : artist_ids
            }
    return render(request, 'recommender/results.html', context)

#About Page
def about(request):
    return render(request, 'about.html', {})

#Survey Page
def survey(request):   
    return render(request, 'Survey/survey.html', {})
