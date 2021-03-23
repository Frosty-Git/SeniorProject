import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import client_credentials as client_cred
import search

scope = "playlist-modify-public"
client_cred.setup()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

#results = sp.current_user_saved_tracks()
# for idx, item in enumerate(results['items']):
#     track = item['track']
#     print(idx, track['artists'][0]['name'], " – ", track['name'])

#sp.user_playlist_create(username, 'test', public=True, collaborative=False, description="This is a test")
# playlist = sp.current_user_playlists(limit=1)

# sp.user_playlist_add_tracks(username, playlist_id['id'], tracks=['spotify:track:0EUNw5Uk0xEcYuCAJmZXhL'])

print(search.search_audio_features("Hello Adele"))