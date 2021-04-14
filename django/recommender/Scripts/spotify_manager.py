import time
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.conf import settings
import recommender.Scripts.client_credentials as client_cred
from user_profile.models import *

class SpotifyManager:
    def __init__(self):
        client_cred.setup()
        self.scope = ('user-read-recently-played user-top-read user-read-playback-position '
            'playlist-modify-public playlist-modify-private playlist-read-private '
            'playlist-read-collaborative user-library-modify user-library-read '
            'streaming user-read-email user-read-private user-modify-playback-state '
            'user-read-playback-state user-read-currently-playing')
        self.auth_manager = spotipy.oauth2.SpotifyOAuth(scope=self.scope, show_dialog=True, redirect_uri='http://localhost:8000/user/save_token_redirect')

    def create_spotify(self):
        spotify = spotipy.Spotify(auth_manager=self.auth_manager)
        return spotify

    def token_check(self, request):
        user = UserProfile.objects.get(user=request.user.id)
        
        if(int(user.expires_at) - int(time.time()) <= 0):
            token_info = self.auth_manager.refresh_access_token(user.refresh_token)
            
            user.access_token = token_info['access_token']
            user.refresh_token = token_info['refresh_token']
            user.expires_at = token_info['expires_at']
            user.save()
            os.remove(os.path.abspath(".cache"))
        
        
        