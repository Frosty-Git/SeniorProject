from recommender.forms import SearchForm
from django.shortcuts import render
from django.http import Http404
from .models import *
from .forms import *
from django.views.decorators.http import require_POST, require_GET
import numpy as np
from recommender.Scripts.search import search_albums, search_artists, search_tracks, search_audio_features
from django.contrib.auth.models import User
from user_profile.models import *
import re

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
        'name': 'PengBeats',
        'ourSearchForm': ourSearchForm,
    }
    return render(request, 'home.html', context)

# Search Results Page
def results(request):

    if request.method == "POST":
        form = OurSearchForm(request.POST)
        if form.is_valid():
            term = request.POST.get('term')
            track1_ids = search_tracks(term, 5, 0)
            track2_ids = search_tracks(term, 5, 4)
            track3_ids = search_tracks(term, 5, 9)
            
            album1_ids = search_albums(term, 5, 0)
            album2_ids = search_albums(term, 5, 4)
            album3_ids = search_albums(term, 5, 9)

            artist1_ids = search_artists(term, 5, 0)
            artist2_ids = search_artists(term, 5, 4)
            artist3_ids = search_artists(term, 5, 9)
            
            features = search_audio_features(term)

            playlists = []
            if request.user.id is not None:
                user_id = request.user.id

                playlists = get_user_playlists(user_id)

            users = search_users(term)

            context = {
                'term' : term,
                'tracks1' : track1_ids,
                'tracks2' : track2_ids,
                'tracks3' : track3_ids,
                'albums1' : album1_ids,
                'albums2' : album2_ids,
                'albums3' : album3_ids,
                'artists1' : artist1_ids,
                'artists2' : artist2_ids,
                'artists3' : artist3_ids,
                'features' : features,
                'playlists' : playlists,
                'users' : users,
            }
    return render(request, 'recommender/results.html', context)

#About Page
def about(request):
    return render(request, 'about.html', {})

#Survey Page
def survey(request):   
    return render(request, 'Survey/survey.html', {})

# This Week's Top Tracks
def top_tracks(request):
    """
    The view for This Week's Top Songs Page
    Author:  Joseph Frost
    Version: 2021.03.18
    """
    context = {}
    return render(request, 'recommender/top-tracks.html', context)

def get_user_playlists(user_id):
    """
    Gets all playlists for a user. Used here so that a song can be added to
    the playlists.
    Last updated: 3/24/21 by Jacelynn Duranceau
    """
    you = UserProfile.objects.get(pk=user_id)
    playlists = Playlist.objects.filter(user_profile_fk=you)
    return playlists

def search_users(term):
    """
    Used to search for a user based on the term entered in the main search page.
    This function is called by the results function above so that it can be 
    passed into the context and returned for display in HTML. 
    It uses a very basic regex that will match the term with any username that
    contains the string of characters in it. If I search 'ace' then users by the
    name of 'jacelynn', 'ace', 'racecar', 'aceofspades', etc. will be returned,
    too.
    Last updated: 3/24/21 by Jacelynn Duranceau
    """
    regex = '.*'+term+'.*'
    users = User.objects.filter(username__regex=regex)[:15]
    user_profiles = []
    for user in users:
        user_profiles.append(UserProfile.objects.get(user=user.id))
    return user_profiles