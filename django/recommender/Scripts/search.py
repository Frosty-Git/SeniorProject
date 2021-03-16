import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import recommender.Scripts.client_credentials as client_cred

client_cred.setup()
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

RESULTS_RETURNED = 5

def search_tracks(query):
    track_ids=[]
    result = sp.search(q=query, limit=RESULTS_RETURNED, offset=0, type='track', market=None)
    for x in range(RESULTS_RETURNED):
        if x+1 > len(result['tracks']['items']):
            break
        track_ids.append(result['tracks']['items'][x]['id'])
    return track_ids

def search_albums(query):
    album_ids=[]
    result = sp.search(q=query, limit=RESULTS_RETURNED, offset=0, type='album', market=None)
    for y in range(RESULTS_RETURNED):
        if y+1 > len(result['albums']['items']):
            break
        album_ids.append(result['albums']['items'][y]['id'])
    return album_ids

def search_artists(query):
    artist_ids=[]
    result = sp.search(q=query, limit=RESULTS_RETURNED, offset=0, type='artist', market=None)
    for z in range(RESULTS_RETURNED):
        if z+1 > len(result['artists']['items']):
            break
        artist_ids.append(result['artists']['items'][z]['id'])
    return artist_ids
