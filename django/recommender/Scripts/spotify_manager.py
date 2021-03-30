import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.conf import settings
import recommender.Scripts.client_credentials as client_cred

class SpotifyManager:
    def __init__(self):
        client_cred.setup()
        self.scope = ('user-read-recently-played user-top-read user-read-playback-position '
            'playlist-modify-public playlist-modify-private playlist-read-private '
            'playlist-read-collaborative user-library-modify user-library-read')
        self.auth_manager = spotipy.oauth2.SpotifyOAuth(scope=self.scope, show_dialog=True, redirect_uri='http://localhost:8000/user/save_token_redirect')

    def create_spotify(self):
        spotify = spotipy.Spotify(auth_manager=self.auth_manager)
        return spotify

        