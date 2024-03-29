from django.shortcuts import render
from django.http import Http404
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Q
from django.template.loader import render_to_string

from datetime import datetime, timedelta
import pytz
import numpy as np
import re
import random
from random import sample
from collections import Counter

from .models import *
from .forms import *
from user_profile.models import *
from social_feed.models import *
from social_feed.views import *
from recommender.Scripts.search import *
from recommender.Scripts.survey import GenresStack


# global variables for spotify manager
spotify_manager = SpotifyManager()


def home(request):
    """
    Creates the home page. Includes a search bar for searching songs, artists,
    albums, and users. Also allows for live searching with "autocompleted"
    results based on your search.
    """
    ourSearchForm = OurSearchForm()
    url_parameter = request.GET.get("q")
    action = request.GET.get('action')
    track_searches = []
    artist_searches = []
    album_searches = []
    profile = None
    is_premium = False

    if request.user.id is not None:
        user_id = request.user.id
        profile = UserProfile.objects.get(pk=user_id)
        if profile.linked_to_spotify:
            spotify_manager.token_check(request)
            is_premium = profile.is_premium
    
    if url_parameter:
        track_searches = livesearch_tracks(url_parameter)
        artist_searches = livesearch_artists(url_parameter)
        album_searches = livesearch_albums(url_parameter)
        
    if request.is_ajax() and action == 'livesearch':
        livesearch_html = render_to_string(
        template_name="recommender/livesearch.html", 
        context={"track_searches": track_searches,
                "artist_searches": artist_searches,
                "album_searches": album_searches,
                "is_premium": is_premium})

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
        'profile': profile, 
        'is_premium': is_premium
    }
    return render(request, 'home.html', context)

    
def results(request):
    """
    Generates the search results page. Sends up to 15 songs, artists, and albums
    based on a search term. Also sends back matching users of Pengbeats.
    Information about the searching user is sent back, too, since users can
    make song posts, like/dislike songs, and add songs to playlists from this
    page.
    """
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
            if track1_ids:
                artists = get_artists(track1_ids[0])
                track_info = get_track(track1_ids[0])
                name = get_song_name(track1_ids[0])
            else:
                artists = None
                track_info = None
                name = None

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
    This is for providing recommendations based on the user's feature preferences,
    top artists, top track, and genre. A user must have liked at least 10 songs,
    have taken the survey, and have liked songs by at least 3 different artists.
    If a user is linked to Spotify, their top track is pulled randomly from their
    top 5. If not, their top track is a random song off of their Liked Songs
    PengBeats playlist. If again the user is linked to Spotify, it pulls their
    top 3 artists from their top 8. If not, it uses the top 3 most commonly
    occurring artists in the user's PengBeats Liked Songs Playlist. This 
    function will not recommend songs that a user has already liked or disliked.
    In addition, it will not recommend explicit songs if the user has them
    turned off.
    Last updated: 4/24/21 by Jacelynn Duranceau, Tucker Elliott and Joe Frost
    """
    user_id = request.user.id
    user = UserProfile.objects.get(pk=user_id)
    limit = 20 # Limit to the recommender
    num_songs = 9 # Number of songs to send back to the recommender page
    
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
        track_ids = []
        playlists = []
        songs_votes = []
        song_list = []

        artists_genre = get_artists_genres(top_artists_ids)
        genre_to_use = []
        if artists_genre:   # If there was a match of your artists to the recommendation seed genres
            genre_to_use = [artists_genre]
        else:   # Use a random genre from your survey genre results
            prefs = Preferences.objects.get(user_profile_fk=profile)
            genres_list = prefs.genres.split('*')
            genres = genres_list[:-1]
            genre = random.sample(genres, 1)
            genre_to_use = [genre[0]]

        track = [get_top_track(request)]

        preferences = Preferences.objects.get(user_profile_fk=user)
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

        while loop:
            issue = False
            results = get_recommendation(request, limit, top_artists_ids, genre_to_use, track, **pref_dict)
            recommendations = results['recommendations']
            if recommendations:
                for x in range(limit):
                    issue = False
                    if len(track_ids) < num_songs:
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
                if len(track_ids) == num_songs:
                    # No need to get more recommendations because we do not have explicit
                    # songs when we don't want them, and it is not returning songs that
                    # have been liked or disliked.
                    loop = False
                else:
                    # Get more songs next time since we failed to get num_songs (9) songs
                    pass
            else:
                success = False
                loop = False

        if len(track_ids) == num_songs:
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


def about(request):
    """
    Renders the About page.
    """
    return render(request, 'about.html', {})


def top_tracks(request):
    """
    Renders the This Week's Top Songs Page
    Last updated: 3/18/21 by Joseph Frost
    """
    context = {}
    return render(request, 'recommender/top-tracks.html', context)


def get_user_playlists(user_id):
    """
    Gets all playlists for a user. Used so that a song can be added to the user's
    playlists.
    Last updated: 3/24/21 by Jacelynn Duranceau
    """
    you = UserProfile.objects.get(pk=user_id)
    playlists = Playlist.objects.filter(user_profile_fk=you)
    return playlists


def search_users(term, requesting_user):
    """
    Used to search for a user based on the term entered in the main search page.
    This function is called by the results function above so that it can be 
    passed into the context and returned for display in HTML. Matches are deter-
    mined by whether the search term is contained in a user's username, first
    name, or last name.
    Last updated: 3/24/21 by Jacelynn Duranceau
    """
    users = User.objects.filter(Q(username__icontains=term) | Q(first_name__icontains=term) | Q(last_name__icontains=term))[:15]
    user_profiles = []
    for user in users:
        # Makes it so that you don't show up in the search results
        if user.id != requesting_user:
            user_profiles.append(UserProfile.objects.get(user=user.id))
    return user_profiles


@require_POST
def searchArtist_post(request):
    """
    This is the artist analyzer. It gets the top and low tracks of artists for
    music features like danceability, energy, etc.
    Last updated: 4/20/21 by James Cino
    """
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
            # Retrieve the queried artist from the cleaned data and get their artistID.
            cd = form.cleaned_data
            artist = cd['artist_name']
            artistID = search_artists(artist, 1, 0)[0]

            # Get their songs with the highest/lowest:
            
            #  Acousticness
            highAcous = search_artist_features(artist, features[0], True)
            lowAcous = search_artist_features(artist, features[0], False)
            #  Danceability
            highDance = search_artist_features(artist, features[1], True)
            lowDance = search_artist_features(artist, features[1], False)
            #  Energy
            highEnergy = search_artist_features(artist, features[2], True)
            lowEnergy = search_artist_features(artist, features[2], False)
            #  Instrumentalness
            highInst = search_artist_features(artist, features[3], True)
            lowInst = search_artist_features(artist, features[3], False)
            #  Speechiness
            highSpeech = search_artist_features(artist, features[4], True)
            lowSpeech = search_artist_features(artist, features[4], False)
            #  Loudness
            highLoud = search_artist_features(artist, features[5], True)
            lowLoud = search_artist_features(artist, features[5], False)
            #  Tempo
            highTempo = search_artist_features(artist, features[6], True)
            lowTempo = search_artist_features(artist, features[6], False)
            #  Valence
            highVal = search_artist_features(artist, features[7], True)
            lowVal = search_artist_features(artist, features[7], False)
            
            form = ArtistForm()

            # Dictionaries to organize the data for the carousels
            # Assigns the track variables to their extreme feature

            highTracks1 = {
                highDance: features[1], 
                highAcous: features[0],
                highEnergy: features[2], 
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
                lowEnergy: features[2], 
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
                'artist': artist,
                'id' : artistID,
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
    """
    Used to search for an artist for the above artist analyzer.
    Last updated: 4/20/21 by James Cino
    """
    form = ArtistForm()
    return render(request, 'recommender/artist.html', {'form': form})


@require_POST
def searchSong_post(request):
    """
    This analyzers a song's music features values like the danceability, energy,
    etc.
    Last updated: 4/20/21 by James Cino
    """
    # process the form data
    if request.method == 'POST':
        # create a form instance and populate it
        form = SongForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            #Get the queried song and its features
            name = cd['song_title']
            features = search_audio_features(name)

            # Seperate the track features into their own variables
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
    """
    Used to search for a song for the above song analyer.
    Last updated: 4/20/21 by James Cino
    """
    form = SongForm()
    return render(request, 'recommender/song.html', {'form': form})


def song_upvote(request):
    """
    Upvotes a song.
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
    Downvotes a song.
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
    Adds a song to a user's My Liked Songs playlist upon a like.
    Last updated: 4/1/21 by Jacelynn Duranceau
    """
    song = SongId.objects.get(pk=track)
    liked_songs_playlist = user_profile.liked_songs_playlist_fk
    new_song = SongOnPlaylist(playlist_from=liked_songs_playlist, spotify_id=song)
    new_song.save()


def rm_from_liked_songs(user_profile, track):
    """
    Removes a song from a user's My Liked Songs playlist upon a dislike.
    Last updated: 4/1/21 by Jacelynn Duranceau
    """
    song = SongId.objects.get(pk=track)
    liked_songs_playlist = user_profile.liked_songs_playlist_fk
    # This will only be one song since a user cannot manually add songs to the playlist,
    # so there is no issue of a duplicate playlist/song match
    sop = SongOnPlaylist.objects.filter(playlist_from=liked_songs_playlist, spotify_id=song).first()
    if sop is not None:
        sop.delete()


def survey_genres(request):
    """
    Renders the initial genres survey page.
    Last updated: 4/8/21 by Joseph Frost, Katie Lee, Jacelynn Duranceau
    """
    user_id = request.user.id
    user = UserProfile.objects.get(pk=user_id)
    if user.survey_taken:
        messages.warning(request, ('Warning: Taking the survey again will reset your preferences!'))
    return render(request, 'Survey/survey_genres.html', {})


def create_genre_stack(request):
    """
    Creates the stack for genres that the user selected. It is generated as a 
    string so that it can be passed to the URL. These will be popped off when 
    the user selects the artists and corresponding to that genre until they 
    complete the survey.
    Last updated: 4/8/21 by Joseph Frost, Katie Lee, Jacelynn Duranceau
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
    """
    Gets the artists for the current genre in the stack the user is on for the
    survey. Pulls the artists from a top Spotify playlist corresponding to said
    genre. 
    Last updated: 4/8/21 by Joseph Frost, Katie Lee, Jacelynn Duranceau
    """
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
    Sends the artists the user selected to the song page so that the survey will
    generate songs for the user to pick by those artists.
    Last updated: 4/8/21 by Joseph Frost, Katie Lee, Jacelynn Duranceau
    """
    artists = request.POST.getlist('artist_id_list[]')
    new_genre_stack = GenresStack(genre_stack, artists, songs_list)
    artists_string = new_genre_stack.artistsToString()
    link = 'survey_songs/' + new_genre_stack.genresToString() + '/' + artists_string + '/' + songs_list
    response = {'redirect' : link}
    return JsonResponse(response)


def survey_songs(request, genre_stack, artists_string, songs_list):
    """
    Generates songs for the user to pick in the survey corresponding to the 
    genre/artists they picked.
    Last updated: 4/8/21 by Joseph Frost, Katie Lee, Jacelynn Duranceau, James Cino
    """
    if '*' in artists_string:
        artists = artists_string.split('*')
        # Last result is an empty string, so pop it off
        artists.pop()

    track_ids = []
    track_names = []
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
    """
    Checks to see if there are any genres left in the stack. So, it determines
    whether the survey is completed or if we need to move onto the artists for
    the next genre in the stack.
    Last updated: 4/8/21 by Joseph Frost, Katie Lee, Jacelynn Duranceau
    """
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
    """
    Saves all of the songs the user selected from the survey, and sets the user's
    preferences to the average of all the music feauture values for those songs.
    Redirects the user to get their recommendations. If they did not choose
    enough songs and artists (up to 3 genres, up to 3 artists per genre, and 5 
    songs per 3 artists), then they might not be able to get recommendations right
    away. This also automatically makes the user like the songs they selected,
    so they will be added to the Liked Songs playlist.
    Last updated: 4/8/21 by Joseph Frost, Katie Lee, Jacelynn Duranceau
    """
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
    """
    Determines the top playlists from the past 7 days. It is based on the likes
    said playlists have received in that time frame.
    Last updated: 4/20/21 by Joseph Frost, Katie Lee
    """
    days_to_subtract = 7
    num_top_playlists = 10
    top_playlists = {}
    
    # Get all of the likes for the playlists from the past week
    d = datetime.datetime.now(pytz.utc)- timedelta(days=days_to_subtract)
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
    Gets artists related to an artist and his/her top songs and albums. 
    Last updated: 4/12/21 by Jacelynn Duranceau
    """
    all_related_artists = get_all_related_artists(artist_id)
    if len(all_related_artists) > 12:
        related_artists = random.sample(all_related_artists, k=12)
    else:
        related_artists = all_related_artists
    
    related_artists_dict = {}
    for artist in related_artists:
        related_artists_dict[artist] = get_artist_name(artist)
        
    top_tracks = get_top_tracks(artist_id)
    save_songs(top_tracks)
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
            'related_artists': related_artists_dict,
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
            'related_artists': related_artists_dict,
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
    if user_id is not None:
        user = UserProfile.objects.get(pk=user_id)
        # liked_songs = user.liked_songs_playlist_fk
        # sop = SongOnPlaylist.objects.filter(playlist_from=liked_songs)
    else:
        user = None
        # liked_songs = []
        # sop = []
    input_artist_ids = request.POST.getlist('artist_id_list[]')
    input_track_ids = request.POST.getlist('track_id_list[]')
    genre = request.POST.getlist('genre_list[]')
    features = request.POST.getlist('feature_list[]')
    limit = 20
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

    loop = True
    issue = False
    track_ids = []
    while loop:
        issue = False
        results = get_custom_recommendation(request, limit, input_artist_ids, input_track_ids, genre, **pref_dict)
        recommendations = results['recommendations']
        for x in range(limit):
            if len(track_ids) < 9:
                if x+1 > len(recommendations['tracks']):
                    break
                track_id = recommendations['tracks'][x]['id']
                save_songs([track_id])
                if user is not None:
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
        if len(track_ids) == 9:
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


def generate_results(request, track_string):
    """
    Generates the results for the custom recommender.
    Last updated: 4/21/21 by Jacelynn Duranceau
    """
    track_ids = track_string.split("*")
    track_ids.pop() # Remove the empty string from the query string
    user_id = request.user.id
    song_list = track_ids
    if user_id is not None:
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
    else:
        context = {
            'track_ids' : song_list,
            'location': 'recommender',
        }
    return render(request, 'recommender/custom_recommender_results.html', context)


def spotify_stats(request):
    """
    If the user is linked to Spotify, they can get their stats for the site.
    Specifically, their top 9 songs and artists.
    Last updated: 4/22/21 by Jacelynn Duranceau, Kevin Magill
    """
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
        except Exception as e: # A user doesn't even have 9 top songs to choose from
            print(e)
            track_error = True
    else:
        # This view function should not be called for a user not linked! It is
        # set up so that they can't, but just in case.
        pass

    if track_ids:
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
    else:
        context = {
            'profile': user,
        }

    return render(request, 'recommender/spotify_stats.html', context)

