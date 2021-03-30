import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import recommender.Scripts.client_credentials as client_cred

client_cred.setup()
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

#RESULTS_RETURNED = 5

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
    Enter in an artist name. Returns the audio features of that song.
    Make sure to be very specific with your query to get the correct
    song. These are the same audio features for the Kaggle data.
    """
    current_max = None
    current_min = None

    high_song = None
    low_song = None

    songs = sp.search(q='artist:' + query, type='track')['tracks']['items']
    num_songs = len(songs)
    for X in range(num_songs):
        song_feats = sp.audio_features(songs[X]['id'])
        level = song_feats[0].get(feature)

        if current_min is None:
             current_min = level
        if current_max is None:
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
        
def get_artists(track):
    """
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
        
def get_song_name(track):
    """
    """
    name = sp.track(track)['name']
    return name

def get_track(track):
    info = sp.track(track)
    return info
