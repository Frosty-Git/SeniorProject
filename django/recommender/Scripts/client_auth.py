import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import client_credentials as client_cred
import search

"""
This script is for the website to be able to use the spotify api
without having the user login to their account. It uses our company's 
PengBeats spotify account.
"""

scope = "playlist-modify-public"
client_cred.setup()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))