import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import recommender.Scripts.client_credentials as client_cred
from user_profile.models import *
from collections import Counter
import re
from recommender.Scripts.spotify_manager import SpotifyManager
import random

client_cred.setup()
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)


def search_tracks(query, RESULTS_RETURNED, offset):
    """
    Searches Spotify for tracks that match the query.
    Returns the number of results specified in RESULTS_RETURNED.
    The offset changes the starting index of the returned results.
    """
    track_ids=[]
    result = sp.search(q=query, limit=RESULTS_RETURNED, offset=offset, type='track', market=None)
    for x in range(RESULTS_RETURNED):
        if x+1 > len(result['tracks']['items']):
            break
        track_ids.append(result['tracks']['items'][x]['id'])
    return track_ids


def search_albums(query, RESULTS_RETURNED, offset):
    """
    Searches Spotify for albums that match the query.
    Returns the number of results specified in RESULTS_RETURNED.
    The offset changes the starting index of the returned results.
    """
    album_ids=[]
    result = sp.search(q=query, limit=RESULTS_RETURNED, offset=offset, type='album', market=None)
    for y in range(RESULTS_RETURNED):
        if y+1 > len(result['albums']['items']):
            break
        album_ids.append(result['albums']['items'][y]['id'])
    return album_ids


def search_artists(query, RESULTS_RETURNED, offset):
    """
    Searches Spotify for artists that match the query.
    Returns the number of results specified in RESULTS_RETURNED.
    The offset changes the starting index of the returned results.
    """
    artist_ids=[]
    result = sp.search(q=query, limit=RESULTS_RETURNED, offset=offset, type='artist', market=None)
    for z in range(RESULTS_RETURNED):
        if z+1 > len(result['artists']['items']):
            break
        artist_ids.append(result['artists']['items'][z]['id'])
    return artist_ids


def search_audio_features(query):
    """
    Enter in a song name. Returns the audio features of that song.
    Make sure to be very specific with your query to get the correct
    song. These are the same audio features for the Kaggle data.
    """
    track = search_tracks(query, 1, 0)
    features = sp.audio_features(tracks=track)
    return features


def get_audio_features(track):
    """
    Track should be a single song's id in an array. Returns the features of
    said track.
    Last updated: 3/29/21 by Katie Lee, Jacelynn Duranceau, Marc Colin
    """
    features = sp.audio_features(tracks=track)
    return features


def search_artist_features(query, feature, high_or_low):
    """
    Enter in an artist name. 
    Returns the song with the highest or lowest value for that feature.
    These are the same audio features for the Kaggle data.
    Last Updated: 4/23/21 by James Cino
    """
    current_max = None
    current_min = None

    high_song = None
    low_song = None

    # Find every track on Spotify featuring the queried artist
    songs = sp.search(q='artist:' + query, type='track')['tracks']['items']
    num_songs = len(songs)

    # Compare each song to determine which has the highest and lowest value.
    for X in range(num_songs):
        song_feats = sp.audio_features(songs[X]['id'])
        level = song_feats[0].get(feature)

        if current_min is None:
            if level is not None:
                current_min = level
        if current_max is None:
            if level is not None:
                current_max = level
        
        if current_min >= level:
            low_song = songs[X]['id']
            current_min = level
        if current_max <= level:
            high_song = songs[X]['id']
            current_max = level
    
    if high_or_low is True:
        return high_song
    else:
        return low_song


def get_top_tracks(artist_id):
    """
    Gets an artist's top tracks from spotify.
    Last updated: 4/21/21 by Jacelynn Duranceau
    """
    tracks = sp.artist_top_tracks('spotify:artist:'+artist_id)['tracks']
    all_tracks = []
    for track in tracks:
        all_tracks.append(track['id'])

    return all_tracks
        

def get_recommendation(request, limit, seed_artists, genre, track, **kwargs):
    """
    Gets recommendations for a user based on their top songs and artists.
    The first three parameters to the sp.recommendations function must be a list.
    Last updated: 4/20/21 by Jacelynn Duranceau
    """
    top_artist_name = ''
    related_artists_ids = []
    recommendations = []
    if len(seed_artists) >= 1 and len(track) == 1:
        related_artists_ids = get_related_artists(seed_artists[0], 6)
        # 3 artists, 1 genre, 1 track
        recommendations = sp.recommendations(seed_artists=seed_artists,
                                            seed_genres=genre, 
                                            seed_tracks=track, 
                                            limit=limit,
                                            country=None,
                                            **kwargs)
        top_artist_name = get_artist_name(seed_artists[0])
    results = {'related_artists_ids': related_artists_ids, 'recommendations': recommendations, 'top_artist': top_artist_name}
    return results


def get_custom_recommendation(request, limit, artists, track, genre, **kwargs):
    """
    Gets a user custom recommendations based on input from the custom
    recommender page. Artists, track, genre, and features (**kwargs)
    must be sent in as a list.
    Last updated: 4/21/21 by Jacelynn Duranceau
    """
    recommendations = sp.recommendations(seed_artists=artists,
                                        seed_genres=genre, 
                                        seed_tracks=track, 
                                        limit=limit,
                                        country=None,
                                        **kwargs)
    results = {'recommendations': recommendations}
    return results


def get_top_artists_by_id(request):
    """
    Gets the top 3 artists ids from a user's liked songs if not linked to spotify.
    If linked, choose a random 3 of the top 8.
    Last updated: 4/19/21 by Jacelynn Duranceau 
    """
    user_id = request.user.id
    user = UserProfile.objects.get(pk=user_id)
    if user.linked_to_spotify:
        spotify_manager = SpotifyManager()
        spotify_manager.token_check(request)
        spotify = spotipy.Spotify(auth=user.access_token)
        try:
            top_artists = spotify.current_user_top_artists(limit=8, offset=0, time_range='long_term')['items']
            random_artists = []
            if len(top_artists) > 3:
                random_artists = random.sample(top_artists, 3)['id']
            else:
                return random_artists[0]['id']
            return random_artists
        except: # A user doesn't even have 8 top artists to choose from
            return get_top_pengbeats_artists(user)
    else:
        return get_top_pengbeats_artists(user)


def get_top_pengbeats_artists(user):
    """
    Gets the top 3 artists for a user on Pengbeats
    Last updated: 4/19/21 by Jacelynn Duranceau
    """
    liked_songs = user.liked_songs_playlist_fk
    matches = SongOnPlaylist.objects.filter(playlist_from=liked_songs).values()
    songs = []

    for match in matches:
        song_id = match.get('spotify_id_id')
        songs.append(song_id)

    all_artists = []
    for song in songs:
        artists = get_artists_ids_list(song)
        for artist_id in artists: 
            if not get_artist_name(artist_id) == 'Various Artists':
                all_artists.append(artist_id)

    # Dictionary for frequency
    top_3_artists = []
    if len(all_artists) >= 1:
        frequency = Counter(all_artists)
        most_common = frequency.most_common(3)
        top_3_artists = [key for key, val in most_common]

    return top_3_artists


def get_artists_genres(artist_id_list):
    """
    Gets the most common genre among your top 3 artists if it appears in the 
    genre seeds
    Last updated: 4/1/21 by Jacelynn Duranceau
    """
    artists_features = get_artists_features(artist_id_list)['artists']
    all_genres = []
    for artist in artists_features:
        genres = artist['genres']
        for genre in genres:
            all_genres.append(genre)

    genre_seeds = sp.recommendation_genre_seeds()['genres']

    matching_genres = []
    for genre in all_genres:
        if genre in genre_seeds:
            matching_genres.append(genre)

    if matching_genres:
        frequency = Counter(matching_genres)
        most_common = frequency.most_common() # [(genre, frequency)]
        return most_common[0][0]
    else:
        return []


def get_related_artists(artist_id, num):
    """
    Returns random artists related to an artist. Max number is 20.
    Last updated: 4/8/21 by Jacelynn Duranceau
    """
    artists = sp.artist_related_artists(artist_id)['artists']
    all_artists = []
    for artist in artists:
        all_artists.append(artist['id'])
    if len(all_artists) > num:
        random_artists = random.sample(all_artists, num)
    else:
        random_artists = all_artists
    return random_artists


def get_all_related_artists(artist_id):
    """
    Returns all artists related to an artist.
    Last updated: 4/12/21 by Jacelynn Duranceau
    """
    artists = sp.artist_related_artists(artist_id)['artists']
    all_artists = []
    for artist in artists:
        all_artists.append(artist['id'])
    return all_artists
    

def get_artists(track):
    """
    Gets the artists of a song as a string list
    Last updated:
    """
    artist_names = []
    artists = sp.track(track)['album']['artists'] # --> [{'key':{}, 'key':string}, {'key':{}, 'key':string}, {for next artist}]
    for dicti in artists:
        artist_names.append(dicti['name'])
    
    size = len(artist_names)
    string_artists = ''
    for i, name in enumerate(artist_names):
        if i != size-1:
            string_artists += (name + ', ')
        else:
            string_artists += name

    return string_artists


def get_artists_features(artists_ids):
    """
    Gets the names of artists from a list of artist ids
    Last updated: 4/1/21 by Jacelynn Duranceau
    """
    artists_features = sp.artists(artists_ids)
    return artists_features


def get_artists_ids_list(track):
    """
    Gets the artists ids of a song in a list / array
    Last updated: 4/1/21 by Jacelynn Duranceau
    """
    artist_names = []
    artists = sp.track(track)['album']['artists'] # --> [{'key':{}, 'key':string}, {'key':{}, 'key':string}, {for next artist}]
    for dicti in artists:
        artist_names.append(dicti['id'])

    return artist_names


def get_artist_name(artist_id):
    """
    Gets the name of an artist based on their id
    """
    name = sp.artist(artist_id)['name']
    return name


def get_artist_image(artist_id):
    """
    Gets the image associated with an artist.
    """
    image = sp.artist(artist_id)['images'][0]['url']
    return image


def get_track(track):
    """
    Gets a lot of information about a track based on its id.
    """
    info = sp.track(track)
    return info


def get_explicit(track):
    """
    Tells whether a song is explicit or not.
    """
    explicit = sp.track(track)['explicit']
    return explicit


def genre_seeds():
    """
    Gets all the genre seeds that can be used in the spotipy recommender
    function.
    """
    seeds = sp.recommendation_genre_seeds()
    return seeds


def get_top_track(request):
    """
    Gets the top track of a user
    Last updated: 4/19/21 by Jacelynn Duranceau and Tucker Elliott
    """
    user = UserProfile.objects.get(pk=request.user.id)
    if user.linked_to_spotify:
        spotify_manager = SpotifyManager()
        spotify_manager.token_check(request)
        spotify = spotipy.Spotify(auth=user.access_token)
        try:
            top_tracks = spotify.current_user_top_tracks(limit=5, offset=0, time_range='long_term')['items']
            random_song = random.choice(top_tracks)['id']
            return random_song
        except: # A user doesn't even have 5 top songs to choose from
            return get_random_liked_pengbeats_song(user)
    else:
        return get_random_liked_pengbeats_song(user)


def get_random_liked_pengbeats_song(user):
    """
    Select a random track from a user's liked songs to be used as a parameter
    in the recommender function
    Last updated: 4/19/21 by Jacelynn Duranceau
    """
    liked_songs_playlist = user.liked_songs_playlist_fk
    sop = SongOnPlaylist.objects.filter(playlist_from=liked_songs_playlist)
    random_song = random.choice(sop)
    spotify_id = random_song.spotify_id.spotify_id
    return spotify_id


def get_playlist_items(playlist_id):
    """
    Gets the data associated with a Spotify playlist based on its id. Is used
    by the survey to pull out tracks from Spotify playlists.
    Last updated: 4/8/21 by Joseph Frost, Katie Lee, Jacelynn Duranceau
    """
    return sp.playlist_items(playlist_id, fields=None, limit=50, offset=0, market=None, additional_types=('track', 'episode'))['items']


def livesearch_tracks(query):
    """
    Live searches the tracks based on user input on home
    Last updated: 4/20/21 by Katie Lee
    """
    searches={}
    limit = 5
    result = sp.search(q=query, limit=limit, offset=0, type='track', market=None)
    for x in range(limit):
        new_list = []
        if x+1 > len(result['tracks']['items']):
            break
        new_list.append(result['tracks']['items'][x]['name'])
        new_list.append(result['tracks']['items'][x]['artists'][0]['name'])
        new_list.append(result['tracks']['items'][x]['album']['images'][2]['url'])
        searches[result['tracks']['items'][x]['id']] = new_list
    return searches


def livesearch_artists(query):
    """
    Live searches the artists based on user input on home
    Last updated: 4/20/21 by Katie Lee
    """
    searches={}
    limit = 3
    result = sp.search(q=query, limit=limit, offset=0, type='artist', market=None)
    for x in range(limit):
        new_list = []
        if x+1 > len(result['artists']['items']):
            break
        new_list.append(result['artists']['items'][x]['name'])
        try:
            picture = result['artists']['items'][x]['images'][0]['url']
        except:
            picture = None
        new_list.append(picture)
        searches[result['artists']['items'][x]['id']] = new_list
    return searches


def livesearch_albums(query):
    """
    Live searches the albums based on user input on home
    Last updated: 4/20/21 by Katie Lee
    """
    searches={}
    limit = 3
    result = sp.search(q=query, limit=limit, offset=0, type='album', market=None)
    for x in range(limit):
        new_list = []
        if x+1 > len(result['albums']['items']):
            break
        new_list.append(result['albums']['items'][x]['name'])
        new_list.append(result['albums']['items'][x]['artists'][0]['name'])
        try:
            picture = result['albums']['items'][x]['images'][0]['url']
        except:
            picture = None
        new_list.append(picture)
        searches[result['albums']['items'][x]['id']] = new_list
    return searches


def get_song_duration(track_id):
    """
    Gets the length of a song in ms.
    Last updated: 4/14/21 by Jacelynn Duranceau
    """
    info = get_track(track_id)
    duration = info['duration_ms']
    return duration


def get_song_album(track_id):
    """
    Gets the name of the album a song appears on
    Last updated: 4/14/21 by Jacelynn Duranceau
    """
    info = get_track(track_id)
    album = info['album']['name']
    return album


def get_song_name(track):
    """
    Gets the name of a song based on its id
    Last updated: 4/14/21 by Jacelynn Duranceau
    """
    info = get_track(track)
    name = info['name']
    return name


def get_album_image(track):
    """
    Gets the album image associated with a track by its id
    Last updated: 4/14/21 by Jacelynn Duranceau
    """
    info = get_track(track)
    album_image = info['album']['images'][0]['url']
    return album_image


def get_artist_albums(art_id):
    """
    Gets the albums from an artist based on their id. Gets up to 12 total.
    Last updated: 4/14/21 by Jacelynn Duranceau
    """
    album_ids = {}
    albums = sp.artist_albums(artist_id=art_id,album_type=None, country=None, limit=12, offset=0)['items']
    for album in albums:
        # The name will serve as the key because spotipy is returning the same
        # albums under a different id for some reason. So, if you encounter 
        # the same album twice, override the previous id with the new one
        album_ids[album['name']] = album['id']

    ids = list(album_ids.values())

    album_ids2 = {}
    if len(ids) < 12:
        albums = sp.artist_albums(artist_id=art_id,album_type=None, country=None, limit=12, offset=12)['items']
        for album in albums:
            album_id = album['id']
            album_name = album['name']
            if album_name not in album_ids.keys():
                album_ids2[album_name] = album_id
    
    ids2 = list(album_ids2.values())

    ids.extend(ids2)
    if len(ids) > 12:
        ids = random.sample(ids, 12)

    return ids