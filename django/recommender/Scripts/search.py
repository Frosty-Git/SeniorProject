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

def search_artist_features(query, feature):
    """
    Enter in an artist name. Returns the audio features of that song.
    Make sure to be very specific with your query to get the correct
    song. These are the same audio features for the Kaggle data.
    """
    current_max = None
    current_min = None

    high_song = None
    low_song = None

    artist = search_artists(query, 1, 0)
    songs = sp.search(q='artist:' + artist, type='track')
    for song in songs:
        song_feats = search_audio_features(song)
        level = song_feats[0].get(feature)

        if current_min is None:
            current_min = level
        if current_max is None:
            current_max = level
        
        if current_min >= level:
            low_song = song
            current_min = level
        if current_max <= level:
            high_song = song
            current_max = level
    
    results = [low_song, high_song]
    return results
        

        
