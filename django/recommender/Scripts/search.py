RESULTS_RETURNED = 10
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

def search_tracks(query):
    track_ids=[]
    result = sp.search(q=query, limit=RESULTS_RETURNED, offset=0, type='track', market=None)
    for x in range(RESULTS_RETURNED):
        if x+1 > len(result['tracks']['items']):
            break
        track_ids.append(result['tracks']['items'][x]['id'])

def search_albums(query):
    album_ids=[]
    result = sp.search(q='abbey%20road', limit=RESULTS_RETURNED, offset=0, type='album', market=None)
    for y in range(RESULTS_RETURNED):
        if y+1 > len(result['albums']['items']):
            break
        album_ids.append(result['albums']['items'][y]['id'])

def search_artists(query):
    artist_ids=[]
    result = sp.search(q='dog', limit=RESULTS_RETURNED, offset=0, type='artist', market=None)
    for z in range(RESULTS_RETURNED):
        if z+1 > len(result['artists']['items']):
            break
        artist_ids.append(result['artists']['items'][z]['id'])