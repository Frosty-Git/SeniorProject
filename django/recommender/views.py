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
from django.contrib import messages
from collections import Counter
import random
from random import sample
from recommender.Scripts.survey import GenresStack
from datetime import datetime, timedelta
import pytz
from django.db.models import Count, Q
from django.template.loader import render_to_string


# global variables for spotify manager
spotify_manager = SpotifyManager()

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
    url_parameter = request.GET.get("q")
    action = request.GET.get('action')
    track_searches = []
    artist_searches = []
    album_searches = []
    profile = None

    if request.user.id is not None:
        user_id = request.user.id
        profile = UserProfile.objects.get(pk=user_id)
        if profile.linked_to_spotify:
            spotify_manager.token_check(request)
    
    if url_parameter:
        track_searches = livesearch_tracks(url_parameter)
        artist_searches = livesearch_artists(url_parameter)
        album_searches = livesearch_albums(url_parameter)
        
    if request.is_ajax() and action == 'livesearch':
        livesearch_html = render_to_string(
        template_name="recommender/livesearch.html", 
        context={"track_searches": track_searches,
                "artist_searches": artist_searches,
                "album_searches": album_searches})

        data_dict = {
            "livesearch_h": livesearch_html,
        }
        return JsonResponse(data=data_dict, safe=False)

    context={
        'name': 'PengBeats',
        'ourSearchForm': ourSearchForm,
        'track_searches': track_searches,
        'artist_searches': artist_searches,
        'album_searches': album_searches,
        'profile': profile
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
                    'location': 'results',
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
                'location': 'results',
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
    survey_taken = False
    min_artists_met = False

    liked_songs = user.liked_songs_playlist_fk
    sop = SongOnPlaylist.objects.filter(playlist_from=liked_songs)
    top_artists_ids = get_top_artists_by_id(request)

    if len(sop) >= 10:              # A user has liked at least 10 songs
        min_likes_met = True
    if user.survey_taken:           # A user has taken the survey
        survey_taken = True
    if len(top_artists_ids) == 3:   # A user has liked songs by at least 3 different artists
        min_artists_met = True

    if min_likes_met and survey_taken:
        loop = True
        issue = False
        success = True # Determines if any results were successfully found
        num_songs = limit
        track_ids = []
        playlists = []
        songs_votes = []
        song_list = []
        while loop:
            issue = False
            results = get_recommendation(request, num_songs, user_id, **pref_dict)
            recommendations = results['recommendations']
            if recommendations:
                print("Getting recs")
                for x in range(num_songs):
                    if len(track_ids) < 9:
                        if x+1 > len(recommendations['tracks']):
                            break
                        track_id = recommendations['tracks'][x]['id']
                        save_songs([track_id])
                        match = SongToUser.objects.filter(user_from=user, songid_to=track_id).first()
                        if match is not None:
                            if match.vote == 'Like' or match.vote == 'Dislike':
                                # The user has already expressed a like or dislike for this
                                # song, so don't recommend it
                                issue = True
                                # break
                        settings = Settings.objects.get(user_profile_fk=user)
                        if settings.explicit_music is False:
                            track = SongId.objects.get(spotify_id=track_id)
                            if track.explicit:
                                # The user does not want songs recommended that are explicit
                                # so don't recommend it
                                issue = True
                                # break
                        if track_id in track_ids:
                            # Don't put a song in the track_ids list if it's already there
                            issue = True
                            # break
                        if not issue:
                            track_ids.append(track_id)
                    else:
                        break
                if not issue:
                    # No need to get more recommendations because we do not have explicit
                    # songs when we don't want them, and it is not returning songs that
                    # have been liked or disliked.
                    loop = False
                else:
                    # Get more recommendations equivalent to the number of songs left
                    # needed in our list limit (of 9); we will loop again
                    # num_songs = (limit - len(track_ids))
                    # loop = True
                    pass
                print(len(track_ids))
            else:
                success = False
                loop = False

        if len(track_ids) == 9:
            playlists = get_user_playlists(user_id)
            songs_votes = SongToUser.objects.filter(user_from=user).values('songid_to_id', 'vote')
            song_list = song_vote_dictionary(songs_votes, track_ids)

        context = {
            'track_ids' : song_list,
            'playlists': playlists,
            'profile': user,
            'top_artists_ids': top_artists_ids,
            'min_likes_met': min_likes_met,
            'min_artists_met': min_artists_met,
            'success': success,
            'location': 'recommender',
            'related_artists': results['related_artists_ids'],
            'top_artist_name': results['top_artist']
        }
    else:
        context = {
            'profile': user,
            'min_likes_met': min_likes_met,
            'min_artists_met': min_artists_met,
            'location': 'recommender',
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
    # regex = '.*'+term+'.*'
    # users = User.objects.filter(username__iregex=regex)[:15]
    users = User.objects.filter(Q(username__icontains=term) | Q(first_name__icontains=term) | Q(last_name__icontains=term))[:15]
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

    features = [
        'acousticness',
        'danceability',
        'energy',
        'instrumentalness',
        'speechiness',
        'loudness',
        'tempo',
        'valence',
    ]

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
            highAcous = search_artist_features(id, features[0], True)
            lowAcous = search_artist_features(id, features[0], False)
            # Get their songs with the highest/lowest Danceability
            highDance = search_artist_features(id, features[1], True)
            lowDance = search_artist_features(id, features[1], False)
            # Get their songs with the highest/lowest Energy
            highLive = search_artist_features(id, features[2], True)
            lowLive = search_artist_features(id, features[2], False)
            # Get their songs with the highest/lowest Energy
            highInst = search_artist_features(id, features[3], True)
            lowInst = search_artist_features(id, features[3], False)
            # Get their songs with the highest/lowest Energy
            highSpeech = search_artist_features(id, features[4], True)
            lowSpeech = search_artist_features(id, features[4], False)
            # Get their songs with the highest/lowest Energy
            highLoud = search_artist_features(id, features[5], True)
            lowLoud = search_artist_features(id, features[5], False)
            # Get their songs with the highest/lowest Energy
            highTempo = search_artist_features(id, features[6], True)
            lowTempo = search_artist_features(id, features[6], False)
            # Get their songs with the highest/lowest Variance
            highVal = search_artist_features(id, features[7], True)
            lowVal = search_artist_features(id, features[7], False)
            
            form = ArtistForm()

            highTracks1 = {
                highDance: features[1], 
                highAcous: features[0],
                highLive: features[2], 
                highInst: features[3]
            }
            highTracks2 = {
                highSpeech: features[4], 
                highLoud: features[5], 
                highTempo: features[6], 
                highVal: features[7]
            } 
            lowTracks1 = {
                lowDance: features[1], 
                lowAcous: features[0], 
                lowLive: features[2], 
                lowInst: features[3]
            }
            lowTracks2 = {
                lowSpeech: features[4], 
                lowLoud: features[5], 
                lowTempo: features[6], 
                lowVal: features[7]
            }

            context = {
                'form': form,
                'artist': id, 
                'highTracks1': highTracks1,
                'highTracks2': highTracks2, 
                'lowTracks1': lowTracks1,
                'lowTracks2': lowTracks2
                }

            return render(request, 'recommender/artist.html', context)
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

            name = cd['song_title']
            features = search_audio_features(name)

            # # Get their songs with the highest/lowest Acousticness
            # #highAcous = find_track(id, 'acousticness', True)
            # highAcous = search_artist_features(id, 'acousticness')[1]
            # lowAcous = search_artist_features(id, 'acousticness')[0]
            # # Get their songs with the highest/lowest Variance
            # highVal = search_artist_features(id, 'valence')[1]
            # lowVal = search_artist_features(id, 'valence')[0]
            # # Get their songs with the highest/lowest Danceability
            # highDance = search_artist_features(id, 'danceability')[1]
            # lowDance = search_artist_features(id, 'danceability')[0]
            # # Get their songs with the highest/lowest Liveness
            # highLive = search_artist_features(id, 'liveness')[1]
            # lowLive = search_artist_features(id, 'liveness')[0]
            # form = ArtistForm()

            track_id = features[0]['id']
            danceability = features[0]['danceability']
            acousticness = features[0]['acousticness']
            energy = features[0]['energy']
            instrumentalness = features[0]['instrumentalness']
            speechiness = features[0]['speechiness']
            loudness = features[0]['loudness']
            tempo = features[0]['tempo']
            valence = features[0]['valence']

            context = {
                'form': form,
                'id': track_id,
                'danceability': danceability,
                'acousticness': acousticness,
                'energy': energy,
                'instrumentalness': instrumentalness,
                'speechiness': speechiness,
                'loudness': loudness,
                'tempo': tempo,
                'valence': valence,
            }
            return render(request, 'recommender/song.html', context)
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
    Upvotes a song
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
    Downvotes a song
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

def survey_genres(request):
    """
    """
    user_id = request.user.id
    user = UserProfile.objects.get(pk=user_id)
    if user.survey_taken:
        messages.warning(request, ('Warning: Taking the survey again will reset your preferences!'))
    return render(request, 'Survey/survey_genres.html', {})

def create_genre_stack(request):
    """
    """
    genres = request.POST.getlist('checked_list[]')
    genres_stack = ""
    artists_list = ""
    songs_list = "*"
    new_genre_stack = GenresStack(genres_stack, artists_list, songs_list)
    
    user_id = request.user.id
    profile = UserProfile.objects.get(pk=user_id)
    prefs = Preferences.objects.get(user_profile_fk=profile)
    genre_prefs_list = ""
    for genre in genres:
        new_genre_stack.push(genre)
        genre_prefs_list += (genre + "*")

    prefs.genres = str(genre_prefs_list)
    prefs.save()
    
    link = 'survey_artists/' + new_genre_stack.genresToString() + '/' + new_genre_stack.songs_list
    response = {'stack' : link}
    return JsonResponse(response)

def survey_artists(request, genre_stack, songs_list):
    new_genre_stack = GenresStack(genre_stack, "", songs_list)
    genre = new_genre_stack.pop()
    
    # Getting the artist ids from Spotify
    if len(genre) > 0:
        playlist_id = new_genre_stack.get_playlist_id(genre)
        track_items = get_playlist_items(playlist_id)
        dicti = {}
        for track_item in track_items:
            artists = track_item['track']['album']['artists']
            for artist in artists:
                artist_name = artist['name']
                artist_id = artist['id']
                if artist_name != "Various Artists":
                    if not artist_id in dicti:
                        dicti[artist_id] = artist_name

        # randomly pick 15 of those artists and put them in the context
        # for the artist choices.
        # Artist ids
        artists = np.random.permutation(list(dicti.keys()))[:15] 

        artist_ids = [] 
        artist_names = []
        for artist in artists:
            artist_ids.append(artist)
            artist_names.append(dicti[artist])

        context = {
            'artist_ids' : artist_ids,
            'artist_names' : artist_names,
            'genre' : new_genre_stack.get_genre_name(genre),
            'genre_stack': new_genre_stack.genresToString(),
            'songs_list': songs_list,
        }
        return render(request, 'Survey/survey_artists.html', context)
    else:
        # Change to recommender
        return HttpResponseRedirect('/')

def send_artists(request, genre_stack, songs_list):
    """
    """
    artists = request.POST.getlist('artist_id_list[]')
    new_genre_stack = GenresStack(genre_stack, artists, songs_list)
    artists_string = new_genre_stack.artistsToString()
    link = 'survey_songs/' + new_genre_stack.genresToString() + '/' + artists_string + '/' + songs_list
    response = {'redirect' : link}
    return JsonResponse(response)

def survey_songs(request, genre_stack, artists_string, songs_list):
    """
    """
    if '*' in artists_string:
        artists = artists_string.split('*')
        # Last result is an empty string, so pop it off
        artists.pop()

    track_ids = []
    track_names = []

    # if genre_stack has next - Joe|| I'm checking if it's empty, same difference but it'll work if we need to pop for some reason. - James
    # if not genre_stack.isEmpty: || On second thought, does it not make more sense to only check if artists isn't empty?
    if len(artists) != 0:
        # for each around the artists
        for artist in artists:
            tracks = get_top_tracks(artist)
            if len(tracks) > 5:
                track_ids.extend(random.sample(tracks, 5))
            else:
                track_ids.extend(tracks)

    for track in track_ids:
        track_names.append(get_song_name(track))

    artist_names = []
    for artist_id in artists:
        artist_names.append(get_artist_name(artist_id))

    context = {
        'track_ids': track_ids,
        'track_names': track_names,
        'genre_stack': genre_stack,
        'artist_names': artist_names,
        'songs_list': songs_list
    }
    return render(request, 'Survey/survey_songs.html', context)

def check_remaining(request, genre_stack, songs_list):
    new_songs = request.POST.getlist('song_id_list[]')
    artist_list = ""

    new_genre_stack = GenresStack(genre_stack, artist_list, songs_list)
    new_genre_stack.extendSongList(new_songs)


    if genre_stack == "*":
        link = 'survey_final/' + new_genre_stack.songs_list
    else:
        link = 'survey_artists/' + new_genre_stack.genresToString() + '/' + new_genre_stack.songs_list
        
    response = {'redirect' : link}
    return JsonResponse(response)
        
def survey_final(request, songs_list):
    genre_stack = ""
    artist_list = ""
    new_genre_stack = GenresStack(genre_stack, artist_list, songs_list)
    tracks = new_genre_stack.songsToList()
    NUM_TRACKS = len(tracks)
    save_songs(tracks)

    # User Preferences:
    danceability = 0
    acousticness = 0
    energy = 0
    instrumentalness = 0
    speechiness = 0
    loudness = 0
    tempo = 0
    valence = 0

    user_id = request.user.id
    user = UserProfile.objects.get(pk=user_id)
    prefs = Preferences.objects.get(user_profile_fk=user)
    user.survey_taken = True
    user.save()

    for track in tracks:
        features = get_audio_features([track])[0]
        danceability += features.get('danceability')
        tempo += features.get('tempo')
        energy += features.get('energy')
        instrumentalness += features.get('instrumentalness')
        loudness += features.get('loudness')
        valence += features.get('valence')
        speechiness += features.get('speechiness')
        acousticness += features.get('acousticness')
        new_song = SongId.objects.get(pk=track)
        vote = SongToUser(user_from=user, songid_to=new_song, vote='Like')
        vote.save()
        add_to_liked_songs(user, track)

    prefs.danceability = danceability / NUM_TRACKS
    prefs.acousticness = acousticness / NUM_TRACKS
    prefs.energy = energy / NUM_TRACKS
    prefs.instrumentalness = instrumentalness / NUM_TRACKS
    prefs.speechiness = speechiness / NUM_TRACKS
    prefs.loudness = loudness / NUM_TRACKS
    prefs.tempo = tempo / NUM_TRACKS
    prefs.valence = valence / NUM_TRACKS
    prefs.save()

    return redirect('/recommendations')

def top_playlists(request):
    days_to_subtract = 7
    num_top_playlists = 10
    top_playlists = {}
    
    # Get all of the likes for the playlists from the past week
    d = datetime.now(pytz.utc)- timedelta(days=days_to_subtract)
    top_playlists_query = FollowedPlaylist.objects.filter(date_created__gte = d).values('playlist_to_id').annotate(total=Count('playlist_to_id')).order_by('-total')[:num_top_playlists]
    
    # The query results are a list of dicts.
    # Convert the query results into a single dict
    for dicti in top_playlists_query:
        playlist = Playlist.objects.get(pk=dicti['playlist_to_id'])
        top_playlists[playlist] = dicti['total']
    
    context = {
        'top_playlists' : top_playlists,
    }

    return render(request, 'recommender/top_playlists.html', context)

def artist_info(request, artist_id):
    """
    Gets artists related to an artist and his/her top songs. 
    Last updated: 4/12/21 by Jacelynn Duranceau
    """
    all_related_artists = get_all_related_artists(artist_id)
    if len(all_related_artists) > 12:
        related_artists = random.sample(all_related_artists, k=12)
    else:
        related_artists = all_related_artists
    top_tracks = get_top_tracks(artist_id)
    name = get_artist_name(artist_id)
    artist_image = get_artist_image(artist_id)
    all_album_ids = get_artist_albums(artist_id)
    user_id = request.user.id
    if user_id is not None:
        playlists = get_user_playlists(user_id)
        profile = UserProfile.objects.get(pk=user_id)
        songs_votes = SongToUser.objects.filter(user_from=profile).values('songid_to_id', 'vote')
        song_list = song_vote_dictionary(songs_votes, top_tracks)
        context = {
            'related_artists': related_artists,
            'top_tracks': song_list,
            'album_ids': all_album_ids,
            'name': name,
            'artist_image': artist_image,
            'playlists': playlists,
            'profile': profile,
            'location': 'artist_page',
        }
    else:
        context = {
            'related_artists': related_artists,
            'top_tracks': top_tracks,
            'album_ids': all_album_ids,
            'name': name,
            'artist_image': artist_image,
        }
    return render(request, 'recommender/artist_info.html', context)

def custom_recommender(request):
    """
    Gets custom recommendations based on user input for up to 3 artists, 1 genre,
    and 1 track.
    Last updated: 4/23/21 by Jacelynn Duranceau
    """
    url_parameter = request.GET.get("q")
    action = request.GET.get('action')
    artist_searches = []
    track_searches = []
    
    if url_parameter:
        if action == 'artist':
            artist_searches = livesearch_artists(url_parameter)
            # Replace the apostrophes because it breaks the custom recommender
            for artist in artist_searches.items():
                s_id = artist[0]
                value = artist[1]
                name = value[0]
                value.append(name)  # artist[3] becomes the original name, to be
                                    # used for displaying in HTML (so that \ does
                                    # not show up)
                if "'" in value[0]:
                    value[0] = name.replace("'", "\\'")

        else: # it's for a track
            track_searches = livesearch_tracks(url_parameter)
            # Replace the apostrophes because it breaks the custom recommender
            for track in track_searches.items():
                s_id = track[0]
                value = track[1]
                name = value[0]
                value.append(name) # the last item in the array becomes the
                                    # original song name for HTML display
                if "'" in value[0]:
                    name = value[0]
                    value[0] = name.replace("'", "\\'")
        
    if request.is_ajax():
        if action == 'artist':
            artists_html = render_to_string(
            template_name="recommender/custom_recommender_artist.html", 
            context={"artist_searches": artist_searches,})

            data_dict = {
                "artist_h": artists_html,
            }
            return JsonResponse(data=data_dict, safe=False)
        else: # it's for a track
            tracks_html = render_to_string(
            template_name="recommender/custom_recommender_track.html", 
            context={"track_searches": track_searches,})

            data_dict = {
                "track_h": tracks_html,
            }
            return JsonResponse(data=data_dict, safe=False)

    context = {
        'artist_searches': artist_searches,
        'track_searches': track_searches
    }
    return render(request, 'recommender/custom_recommender.html', context)

def cust_rec_results(request):
    """
    Generates the results for user selection on the custom recommender.
    Last updated 4/21/21 by Jacelynn Duranceau
    """
    user_id = request.user.id
    user = UserProfile.objects.get(pk=user_id)
    input_artist_ids = request.POST.getlist('artist_id_list[]')
    input_track_ids = request.POST.getlist('track_id_list[]')
    genre = request.POST.getlist('genre_list[]')
    features = request.POST.getlist('feature_list[]')
    limit = 9
    pref_dict = {
        'target_acousticness'     : features[0],
        'target_danceability'     : features[1],
        'target_energy'           : features[2],
        'target_instrumentalness' : features[3],
        'target_speechiness'      : features[4],
        'target_loudness'         : features[5],
        'target_tempo'            : features[6],
        'target_valence'          : features[7],
    }
    
    liked_songs = user.liked_songs_playlist_fk
    sop = SongOnPlaylist.objects.filter(playlist_from=liked_songs)

    loop = True
    issue = False
    num_songs = limit
    track_ids = []
    while loop:
        issue = False
        results = get_custom_recommendation(request, num_songs, user_id, input_artist_ids, input_track_ids, genre, **pref_dict)
        recommendations = results['recommendations']
        for x in range(num_songs):
            if len(track_ids) < 9:
                if x+1 > len(recommendations['tracks']):
                    break
                track_id = recommendations['tracks'][x]['id']
                save_songs([track_id])
                match = SongToUser.objects.filter(user_from=user, songid_to=track_id).first()
                if match is not None:
                    if match.vote == 'Like' or match.vote == 'Dislike':
                        # The user has already expressed a like or dislike for this
                        # song, so don't recommend it
                        issue = True
                settings = Settings.objects.get(user_profile_fk=user)
                if settings.explicit_music is False:
                    track = SongId.objects.get(spotify_id=track_id)
                    if track.explicit:
                        # The user does not want songs recommended that are explicit
                        # so don't recommend it
                        issue = True
                if track_id in track_ids:
                    # Don't put a song in the track_ids list if it's already there
                    issue = True
                if not issue:
                    track_ids.append(track_id)
            else:
                break
        if not issue:
            # No need to get more recommendations because we do not have explicit
            # songs when we don't want them, and it is not returning songs that
            # have been liked or disliked.
            loop = False
        else:
            # Get more recommendations equivalent to the number of songs left
            # needed in our list limit (of 9); we will loop again
            pass

    ugly_string = ""
    for track in track_ids:
        ugly_string += (track + "*")

    link = 'custom_results/' + ugly_string
    response = {'redirect' : link}
    return JsonResponse(response)
    # return render(request, 'recommender/custom_recommender_results.html', context)

def generate_results(request, track_string):
    track_ids = track_string.split("*")
    track_ids.pop() # Remove the empty string from the decoded fake 
                    # query string :) 
                    # PS: Stop using ajax to redirect please.
    user_id = request.user.id
    user = UserProfile.objects.get(pk=user_id)
    playlists = get_user_playlists(user_id)
    songs_votes = SongToUser.objects.filter(user_from=user).values('songid_to_id', 'vote')
    song_list = song_vote_dictionary(songs_votes, track_ids)
    context = {
        'track_ids' : song_list,
        'playlists': playlists,
        'profile': user,
        'location': 'recommender',
    }
    return render(request, 'recommender/custom_recommender_results.html', context)

def spotify_stats(request):
    user_id = request.user.id
    user = UserProfile.objects.get(pk=user_id)

    artist_ids = []
    track_ids = []

    artist_error = False
    track_error = False

    if user.linked_to_spotify:
        spotify_manager = SpotifyManager()
        spotify_manager.token_check(request)
        spotify = spotipy.Spotify(auth=user.access_token)
        try:
            artists = spotify.current_user_top_artists(limit=9, offset=0, time_range='long_term')['items']
            for artist in artists:
                artist_ids.append(artist['id'])
        except Exception as e: # A user doesn't even have 9 top artists to choose from
            print(e)
            artist_error = True
        try:
            tracks = spotify.current_user_top_tracks(limit=9, offset=0, time_range='long_term')['items']
            for track in tracks:
                track_ids.append(track['id'])
        except Exception as e: # A user doesn't even have 15 top songs to choose from
            print(e)
            track_error = True
    else:
        # This view function should not 
        pass

    save_songs(track_ids)

    playlists = get_user_playlists(user_id)
    songs_votes = SongToUser.objects.filter(user_from=user).values('songid_to_id', 'vote')
    song_list = song_vote_dictionary(songs_votes, track_ids)

    context = {
        'profile': user,
        'track_ids': song_list,
        'artist_ids': artist_ids,
        'playlists': playlists,
    }

    return render(request, 'recommender/spotify_stats.html', context)

