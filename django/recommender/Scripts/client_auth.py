import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import client_credentials as client_cred

scope = "playlist-modify-public"
client_cred.setup()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

#results = sp.current_user_saved_tracks()
# for idx, item in enumerate(results['items']):
#     track = item['track']
#     print(idx, track['artists'][0]['name'], " – ", track['name'])

print(sp.me())
username = sp.me()['id']
print(username)
#sp.user_playlist_create(username, 'test', public=True, collaborative=False, description="This is a test")
playlist = sp.current_user_playlists(limit=1)

print(playlist)
playlist_items = playlist['items']
print(playlist_items)
playlist_id = playlist_items[0]
print(playlist_id['id'])

sp.user_playlist_add_tracks(username, playlist_id['id'], tracks=['spotify:track:0EUNw5Uk0xEcYuCAJmZXhL'])
