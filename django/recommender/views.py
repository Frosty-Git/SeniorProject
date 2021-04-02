from recommender.forms import SearchForm
from django.shortcuts import render
from django.http import Http404
from .models import *
from .forms import *
from django.views.decorators.http import require_POST, require_GET
import numpy as np
from recommender.Scripts.search import *
from django.contrib.auth.models import User
from user_profile.models import *
import re
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from social_feed.models import *
from social_feed.views import *
from collections import Counter

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
            
            all_tracks = []
            all_tracks.extend(track1_ids)
            all_tracks.extend(track2_ids)
            all_tracks.extend(track3_ids)
            save_songs(all_tracks)

            album1_ids = search_albums(term, 5, 0)
            album2_ids = search_albums(term, 5, 4)
            album3_ids = search_albums(term, 5, 9)

            artist1_ids = search_artists(term, 5, 0)
            artist2_ids = search_artists(term, 5, 4)
            artist3_ids = search_artists(term, 5, 9)
            
            features = search_audio_features(term)
            artists = get_artists(track1_ids[0])
            track_info = get_track(track1_ids[0])
            name = get_song_name(track1_ids[0])

            user_id = request.user.id
            users = search_users(term, user_id)

            playlists = []
            if user_id is not None:
                song_list_1 = {}
                song_list_2 = {}
                song_list_3 = {}
                playlists = get_user_playlists(user_id)
                loggedin = UserProfile.objects.get(pk=user_id)
                songs_votes = SongToUser.objects.filter(user_from=loggedin).values('songid_to_id', 'vote')
                song_list_1 = song_vote_dictionary(songs_votes, track1_ids)
                song_list_2 = song_vote_dictionary(songs_votes, track2_ids)
                song_list_3 = song_vote_dictionary(songs_votes, track3_ids)

                # These will only work if you have at least one liked song
                # top_artists = get_top_artists_by_name(user_id)
                # top_artists_ids = get_top_artists_by_id(user_id)
                # top_artists_features = get_artists_features(top_artists_ids)
                # top_artists_genres = get_artists_genres(top_artists_ids)
                # genre_seeds_v = genre_seeds()

                context = {
                    'term' : term,
                    'albums1' : album1_ids,
                    'albums2' : album2_ids,
                    'albums3' : album3_ids,
                    'artists1' : artist1_ids,
                    'artists2' : artist2_ids,
                    'artists3' : artist3_ids,
                    'features' : features,
                    'playlists' : playlists,
                    'users' : users,
                    'profile': loggedin,
                    'artists': artists,
                    'track_info': track_info,
                    'song_name': name,
                    'song_list_1': song_list_1,
                    'song_list_2': song_list_2,
                    'song_list_3': song_list_3,
                    # 'top_artists': top_artists,
                    # 'top_artists_ids': top_artists_ids,
                    # 'top_artists_features': top_artists_features,
                    # 'top_artists_genres': top_artists_genres,
                    # 'genre_seeds': genre_seeds_v,
                }
                return render(request, 'recommender/results.html', context)



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
                'artists': artists,
                'track_info': track_info,
                'song_name': name,
            }
    return render(request, 'recommender/results.html', context)

def user_preference_recommender(request):
    """
    This is for providing recommendations based on the user's preferences.
    Last updated: 4/1/21 by Tucker Elliott and Joe Frost
    """
    user_id = request.user.id
    user = UserProfile.objects.get(pk=user_id)
    preferences = Preferences.objects.get(user_profile_fk=user)
    limit = 9
    pref_dict = {
        'target_acousticness'     : preferences.acousticness,
        'target_danceability'     : preferences.danceability,
        'target_energy'           : preferences.energy,
        'target_instrumentalness' : preferences.instrumentalness,
        'target_speechiness'      : preferences.speechiness,
        'target_loudness'         : preferences.loudness,
        'target_tempo'            : preferences.tempo,
        'target_valence'          : preferences.valence,
    }
    
    min_likes_met = False
    liked_songs = user.liked_songs_playlist_fk
    sop = SongOnPlaylist.objects.filter(playlist_from=liked_songs)
    if sop:
        min_likes_met = True

    if min_likes_met:
        recommendations = get_recommendation(request, limit, user_id, **pref_dict)
        track_ids = []
        for x in range(limit):
            if x+1 > len(recommendations['tracks']):
                break
            track_ids.append(recommendations['tracks'][x]['id'])
        playlists = get_user_playlists(user_id)
        top_artists_ids = get_top_artists_by_id(user_id)

        context = {
            'track_ids' : track_ids,
            'playlists': playlists,
            'profile': user,
            'top_artists_ids': top_artists_ids,
            'min_likes_met': min_likes_met,
        }
    else:
        context = {
            'profile': user,
            'min_likes_met': min_likes_met,
    }

    return render(request, 'recommender/user_preference_recommender.html', context)

def song_vote_dictionary(songs_votes, tracks):
    """
    Creates a dictionary that makes the post the key
    and upvote/downvote in a list the value.
    Last updated: 3/30/21 by Katie Lee
    """
    song_list = {}
    for track in tracks:
        up = False
        down = False
        for song in songs_votes:
            if song['songid_to_id'] == track:
                if song['vote'] == 'Like':
                    up = True
                elif song['vote'] == 'Dislike':
                    down = True
        song_list[track] = [up, down]
    return song_list

def save_songs(track_list):
    """
    Save a song to our database if it does not already exist. Is called by the
    results function to save all of the songs that come back for a search query.
    Last updated: 3/30/21 by Marc Colin, Katie Lee, Jacelynn Duranceau
    """
    for track in track_list:
        song = SongId.objects.filter(pk=track).first()
        if song is None:
            features = get_audio_features([track])[0]
            new_song = SongId(pk=track, artists=get_artists(track),
                                        name=get_song_name(track),
                                        explicit=get_explicit(track),
                                        acousticness=features.get('acousticness'), 
                                        danceability=features.get('danceability'),
                                        energy=features.get('energy'),
                                        instrumentalness=features.get('instrumentalness'),
                                        speechiness=features.get('speechiness'),
                                        loudness=features.get('loudness'),
                                        tempo=features.get('tempo'),
                                        valence=features.get('valence'))
            new_song.save()

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

def search_users(term, requesting_user):
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
        # Makes it so that you don't show up in the search results
        if user.id != requesting_user:
            user_profiles.append(UserProfile.objects.get(user=user.id))
    return user_profiles

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
    artist_id = search_artists(artist , 3, 0)
    form = ArtistForm()
    return render(request, 'Survey/survey.html', {'form':form, 'artist_id':artist_id})

def song_upvote(request):
    """
    Counts upvotes for posts
    Last updated: 3/30/21 by Marc Colin, Katie Lee
    """
    track = request.POST.get('track')
    action = request.POST.get('action')
    user = UserProfile.objects.get(pk=request.user.id)
    if track and action:
        song = SongId.objects.get(pk=track)
        if action == 'like':
            vote = SongToUser.objects.filter(user_from=user, songid_to=song).first()
            if vote is None:
                up = SongToUser(user_from=user, songid_to=song, vote="Like")
                up.save()
                change_prefs_song(track, user, "like")
                add_to_liked_songs(user, track)
                return JsonResponse({'status':'ok'})
            else:
                if vote.vote == 'Dislike':
                    change_prefs_song(track, user, "like")
                    vote.vote = 'Like'
                    vote.save()
                    add_to_liked_songs(user, track)                                 
                    return JsonResponse({'status':'switch'}) 
                else:
                    # Took your like away, so remove the song from the My Liked Songs playlist
                    rm_from_liked_songs(user, track)
                    vote.delete()
                    return JsonResponse({'status':'undo_upvote'})
    return JsonResponse({'status':'ko'})

def song_downvote(request):
    """
    Counts upvotes for posts
    Last updated: 3/30/21 by Marc Colin, Katie Lee
    """
    track = request.POST.get('track')
    action = request.POST.get('action')
    user = UserProfile.objects.get(pk=request.user.id)
    if track and action:
        song = SongId.objects.get(pk=track)
        if action == 'dislike':
            vote = SongToUser.objects.filter(user_from=user, songid_to=song).first()
            if vote is None:
                down = SongToUser(user_from=user, songid_to=song, vote="Dislike")
                down.save()
                change_prefs_song(track, user, "dislike")
                rm_from_liked_songs(user, track)
                return JsonResponse({'status':'ok'})
            else:
                if vote.vote == 'Like':
                    change_prefs_song(track, user, "dislike")
                    vote.vote = 'Dislike'
                    vote.save()   
                    rm_from_liked_songs(user, track)                              
                    return JsonResponse({'status':'switch'}) 
                else:
                    vote.delete()
                    return JsonResponse({'status':'undo_downvote'})
    return JsonResponse({'status':'ko'})

def add_to_liked_songs(user_profile, track):
    """
    Adds a song to a user's My Liked Songs playlist
    Last updated: 4/1/21 by Jacelynn Duranceau
    """
    song = SongId.objects.get(pk=track)
    liked_songs_playlist = user_profile.liked_songs_playlist_fk
    new_song = SongOnPlaylist(playlist_from=liked_songs_playlist, spotify_id=song)
    new_song.save()

def rm_from_liked_songs(user_profile, track):
    """
    Removes a song from a user's My Liked Songs playlist
    Last updated: 4/1/21 by Jacelynn Duranceau
    """
    song = SongId.objects.get(pk=track)
    liked_songs_playlist = user_profile.liked_songs_playlist_fk
    # This will only be one song since a user cannot manually add songs to the playlist,
    # so there is no issue of a duplicate playlist/song match
    sop = SongOnPlaylist.objects.filter(playlist_from=liked_songs_playlist, spotify_id=song).first()
    if sop is not None:
        sop.delete()

def get_top_artists_by_name(user_id):
    """
    Gets the top 3 artists from a user's liked songs
    Last updated: 4/1/21 by Jacelynn Duranceau 
    """
    user = UserProfile.objects.get(pk=user_id)
    liked_songs = user.liked_songs_playlist_fk
    matches = SongOnPlaylist.objects.filter(playlist_from=liked_songs).values()
    songs = []

    for match in matches:
        song_id = match.get('spotify_id_id')
        songs.append(song_id)

    all_artists = []
    for song in songs:
        artists = get_artists_names_list(song)
        for artist_name in artists: 
            all_artists.append(artist_name)

    # Dictionary for frequency
    frequency = Counter(all_artists)
    most_common = frequency.most_common(3)
    top_3_artists = [key for key, val in most_common]

    return top_3_artists

# def get_top_artists_by_id(user_id):
#     """
#     Gets the top 5 artists ids from a user's liked songs
#     Last updated: 4/1/21 by Jacelynn Duranceau 
#     """
#     user = UserProfile.objects.get(pk=user_id)
#     liked_songs = user.liked_songs_playlist_fk
#     matches = SongOnPlaylist.objects.filter(playlist_from=liked_songs).values()
#     songs = []

#     for match in matches:
#         song_id = match.get('spotify_id_id')
#         songs.append(song_id)

#     all_artists = []
#     for song in songs:
#         artists = get_artists_ids_list(song)
#         for artist_id in artists: 
#             all_artists.append(artist_id)

#     # Dictionary for frequency
#     frequency = Counter(all_artists)
#     most_common = frequency.most_common(5)
#     top_5_artists = [key for key, val in most_common]

#     return top_5_artists

# def get_artists_features(artist_id_list):
#     """
#     Gets a long list of features about artists
#     Last updated: 4/1/21 by Jacelynn Duranceau
#     """
#     artists_features = get_artists_features_sp(artist_id_list)
#     return artists_features

# def get_artists_genres(artist_id_list):
#     """
#     Gets the top 5 genres from your top 5 artists
#     Last updated: 4/1/21 by Jacelynn Duranceau
#     """
#     artists_features = get_artists_features(artist_id_list)['artists']
#     all_genres = []
#     for artist in artists_features:
#         genres = artist['genres']
#         for genre in genres:
#             all_genres.append(genre)

#     frequency = Counter(all_genres)
#     most_common = frequency.most_common(5)
#     top_5_genres = [key for key, val in most_common]

#     return top_5_genres
