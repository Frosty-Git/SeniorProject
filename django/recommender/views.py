from recommender.forms import SearchForm
from django.shortcuts import render
from django.http import Http404
from .models import *
from .forms import *
from django.views.decorators.http import require_POST, require_GET
import numpy as np
from recommender.Scripts.search import search_albums, search_artists, search_tracks, search_audio_features, search_artist_features

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

#The Analyzer

def find_track(artist, attribute, high):
    # query = Musicdata.objects.filter(artists__contains = artist)
    # results = sp.artist_(artistID)
    if high == True:
        #album = list(results.order_by(-attribute)[0].values('id','name','year'))
        #album = sp.search(q='artist:' + artist, limit=1, offset=0, type="track")

        # album = sp.recommendations(seed_artists=artistID, limit=1, max=attribute) --- Use this one with Spotipy
        album = Musicdata.objects.filter(
            artists__contains=artist).order_by(attribute).last()
    else:
        #album = list(results.order_by(+attribute)[0].values('id','name','year'))
        # album = sp.recommendations(seed_artists=artistID, limit=1, min=attribute) --- Use this one with Spotipy
        album = Musicdata.objects.filter(
            artists__contains=artist).order_by(attribute).first()
    return album

@require_POST
def searchArtist_post(request):
    # process the form data
    if request.method == 'POST':
        # create a form instance and populate it
        form = ArtistForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # Get the artist
            #results = sp.search(cd, 1, 0, "artist")
            #artist = results['artists']['items'][0]
            #id = artist['name']
            id = cd['artist_name']

            # Get their songs with the highest/lowest Acousticness
            highAcous = search_artist_features(id, 'acousticness', True)
            lowAcous = search_artist_features(id, 'acousticness', False)
            # Get their songs with the highest/lowest Variance
            highVal = search_artist_features(id, 'valence', True)
            lowVal = search_artist_features(id, 'valence', False)
            # Get their songs with the highest/lowest Danceability
            highDance = search_artist_features(id, 'danceability', True)
            lowDance = search_artist_features(id, 'danceability', False)
            # Get their songs with the highest/lowest Energy
            highLive = search_artist_features(id, 'energy', True)
            lowLive = search_artist_features(id, 'energy', False)
            form = ArtistForm()

            highTracks = list([highAcous, highVal, highDance, highLive]) 
            lowTracks = list([lowAcous, lowVal, lowDance, lowLive])

            return render(request, 'recommender/artist.html', {'form': form, 'highTracks': highTracks, 'lowTracks': lowTracks})
        else:
            raise Http404('Something went wrong')

@require_GET
def searchArtist_get(request):
    form = ArtistForm()
    return render(request, 'recommender/artist.html', {'form': form})

@require_POST
def searchSong_post(request):
    # process the form data
    if request.method == 'POST':
        # create a form instance and populate it
        form = SongForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # Get the artist
            #results = sp.search(cd, 1, 0, "artist")
            #artist = results['artists']['items'][0]
            #id = artist['name']
            id = cd['artist_name']

            # Get their songs with the highest/lowest Acousticness
            #highAcous = find_track(id, 'acousticness', True)
            highAcous = search_artist_features(id, 'acousticness')[1]
            lowAcous = search_artist_features(id, 'acousticness')[0]
            # Get their songs with the highest/lowest Variance
            highVal = search_artist_features(id, 'valence')[1]
            lowVal = search_artist_features(id, 'valence')[0]
            # Get their songs with the highest/lowest Danceability
            highDance = search_artist_features(id, 'danceability')[1]
            lowDance = search_artist_features(id, 'danceability')[0]
            # Get their songs with the highest/lowest Liveness
            highLive = search_artist_features(id, 'liveness')[1]
            lowLive = search_artist_features(id, 'liveness')[0]
            form = ArtistForm()

            tracks = list([highAcous, highVal, highDance,
                           highLive, lowAcous, lowVal, lowDance, lowLive])

            return render(request, 'recommender/song.html', {'form': form, 'tracks': tracks})
        else:
            raise Http404('Something went wrong')

@require_GET
def searchSong_get(request):
    form = SongForm()
    return render(request, 'recommender/song.html', {'form': form})
    
@require_GET
def get_artist_from_passed_value(request):
    artist = (request.GET['answer'])
    Form = ArtistForm(artist)
    return render(request, 'Survey/survey.html', {'form':form})