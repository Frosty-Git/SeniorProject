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
        self.auth_manager = spotipy.oauth2.SpotifyOAuth(scope=self.scope, redirect_uri='http://localhost:8000/user/token')
        self.spotify = spotipy.Spotify(auth_manager=self.auth_manager)

    def save_token(self, request):
        token_info = self.auth_manager.get_cached_token()
        user_id = request.user.id
        session = request.session.get('_auth_user_id')
        if int(user_id) == int(session):
            if(self.auth_manager.is_token_expired(token_info)):
                self.auth_manager.refresh_access_token(token_info['refresh_token'])
            request.session['_sp_auth_token'] = token_info['access_token']
            sptoken = request.session['_sp_auth_token']
        else:
            request.session['_sp_auth_token'] = None
            sptoken = request.session['_sp_auth_token']
        return sptoken