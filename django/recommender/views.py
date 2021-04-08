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
import random
from random import sample
from recommender.Scripts.survey import GenresStack
from recommender.Scripts.search import get_playlist_items

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
        save_songs(track_ids)
        playlists = get_user_playlists(user_id)
        top_artists_ids = get_top_artists_by_id(user_id)

        songs_votes = SongToUser.objects.filter(user_from=user).values('songid_to_id', 'vote')
        song_list = song_vote_dictionary(songs_votes, track_ids)

        context = {
            'track_ids' : song_list,
            'playlists': playlists,
            'profile': user,
            'top_artists_ids': top_artists_ids,
            'min_likes_met': min_likes_met,
            'location': 'recommender',
        }
    else:
        context = {
            'profile': user,
            'min_likes_met': min_likes_met,
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
            # Get their songs with the highest/lowest Danceability
            highDance = search_artist_features(id, 'danceability', True)
            lowDance = search_artist_features(id, 'danceability', False)
            # Get their songs with the highest/lowest Energy
            highLive = search_artist_features(id, 'energy', True)
            lowLive = search_artist_features(id, 'energy', False)
            # Get their songs with the highest/lowest Energy
            highInst = search_artist_features(id, 'instrumentalness', True)
            lowInst = search_artist_features(id, 'instrumentalness', False)
            # Get their songs with the highest/lowest Energy
            highSpeech = search_artist_features(id, 'speechiness', True)
            lowSpeech = search_artist_features(id, 'speechiness', False)
            # Get their songs with the highest/lowest Energy
            highLoud = search_artist_features(id, 'loudness', True)
            lowLoud = search_artist_features(id, 'loudness', False)
            # Get their songs with the highest/lowest Energy
            highTempo = search_artist_features(id, 'tempo', True)
            lowTempo = search_artist_features(id, 'tempo', False)
            # Get their songs with the highest/lowest Variance
            highVal = search_artist_features(id, 'valence', True)
            lowVal = search_artist_features(id, 'valence', False)
            
            form = ArtistForm()

            highTracks1 = list([highDance, highAcous, highLive, highInst])
            highTracks2 = list([highSpeech, highLoud, highTempo, highVal]) 
            lowTracks1 = list([lowDance, lowAcous, lowLive, lowInst])
            lowTracks2 = list([lowSpeech, lowLoud, lowTempo, lowVal])

            context = {
                'form': form, 
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

def survey_genres(request):
    """
    """
    return render(request, 'Survey/survey_genres.html', {})

def create_genre_stack(request):
    """
    """
    genres = request.POST.getlist('checked_list[]')
    
    genres_stack = ""
    artists_list = ""
    songs_list = ""
    
    new_genre_stack = GenresStack(genres_stack, artists_list)
    for genre in genres:
        new_genre_stack.push(genre)
    # return redirect('recommender:survey_artists', genre_stack=new_genre_stack.toString())
    # return redirect('survey_artists', genre_stack=genre_stack)
    # link = "survey_artists/" + new_genre_stack.toString()
    # data = json.dumps({'url' : link})
    # return HttpResponse(data)
    link = 'survey_artists/' + new_genre_stack.genresToString()
    response = {'stack' : link}
    return JsonResponse(response)

def survey_artists(request, genre_stack):
    new_genre_stack = GenresStack(genre_stack, "")
    genre = new_genre_stack.pop()
    print("HEEEERRRRREE" + new_genre_stack.genresToString())
    print('STACKKKKKKKKK ' + str(new_genre_stack.genres_stack))
    
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
        }
        return render(request, 'Survey/survey_artists.html', context)
    else:
        # Change to recommender
        return HttpResponseRedirect('/')
        # return render(request, "Survey/survey_artists.html", {})

def send_artists(request, genre_stack):
    artists = request.POST.getlist('artist_id_list[]')
    new_genre_stack = GenresStack(genre_stack, artists)
    artists_string = new_genre_stack.artistsToString()
    link = 'survey_songs/' + new_genre_stack.genresToString() + '/' + artists_string 
    response = {'redirect' : link}
    return JsonResponse(response)

def survey_songs(request, genre_stack, artists_string):
    """
    """
    if '*' in artists_string:
        artists = artists_string.split('*')
        # Last result is an empty string, so pop it off
        artists.pop()

    songs_list = [] 
    track_ids = []
    track_names = []
    # art_extreme_tracks = []

    # features = [
    #     'danceability',
    #     'acousticness',
    #     'energy',
    #     'instrumentalness',
    #     'speechiness',
    #     'loudness',
    #     'tempo',
    #     'valence',
    # ]

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

            # for feature in features:
            #     max_feat = search_artist_features(artist, feature, True)
            #     print("MAX")
            #     print(max_feat)
            #     min_feat = search_artist_features(artist, feature, False)
            #     print("MIN")
            #     print(min_feat)
            #     if max_feat not in art_extreme_tracks:
            #         art_extreme_tracks.append(max_feat)     # max value for whatever the current feature is
            #     if min_feat not in art_extreme_tracks:
            #         art_extreme_tracks.append(min_feat)     # min value    

            # if len(art_extreme_tracks) > 5:
            #     # grab a random 5 of the most extreme tracks
            #     var = random.sample(art_extreme_tracks, 5)
            #     print("++++++++++++++++++++++++++++++")
            #     print(var)
            #     track_ids.extend(random.sample(art_extreme_tracks, 5))
            # else:
            #     idk = art_extreme_tracks
            #     print("kjsdhfkjhkfdhsjkdhgkjhdsfghsdkgbsdfgjhbdg")
            #     print(idk)
            #     track_ids.extend(art_extreme_tracks)
            # art_extreme_tracks = []

    # print("======================================")
    # print(track_ids)

    #render survey_artists and context of song list

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
    }
    return render(request, 'Survey/survey_songs.html', context)

def check_remaining(request, genre_stack):
    # songs = request.POST.getlist('song_id_list[]')
    new_genre_stack = GenresStack(genre_stack, [])
    if genre_stack == "*":
        link = ''
        response = {'redirect' : link}
        return JsonResponse(response)
    else:
        link = 'survey_artists/' + new_genre_stack.genresToString()
        response = {'redirect' : link}
        return JsonResponse(response)
        

# Alt-rock → alternative rock
# Alternative
# Anime
# Classical
# Country
# Disco
# Electronic
# Emo
# Folk
# Funk
# Gospel
# Grunge
# Hard-rock → hard rock
# Hip-hop → hip hop
# Indie
# Jazz
# K-pop
# Latin
# Metal
# Pop
# Punk
# R-n-b → r&b
# Reggae
# Rock
# Soul















# This is a sample page for our css styles!
def sample(request):
    return render(request, 'css_sample.html', {})
    
# def update_database_with_preferences(danceability, acousticness, energy, instrumentalness, 
#                                         speechiness, loudness, tempo, valence):
#     if request.method = 'POST':
        

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
