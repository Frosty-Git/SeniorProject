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
        self.caches_folder = './.spotify_caches/'
        if not os.path.exists(self.caches_folder):
            os.makedirs(self.caches_folder)
        auth_manager = None
        cache_handler = None

def session_cache_path(request, spotify_manager):
       return spotify_manager.caches_folder + request.session.get('_auth_user_id')

def index(request, spotify_manager):
    if not request.session.get('_auth_user_id'):
        # If not signed into PengBeats user id is set to none 
        # since it cannot be compared to a Spotify ID
        request.session['_auth_user_id'] = None
    
    spotify_manager.cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path(request, spotify_manager))
    spotify_manager.auth_manager = spotipy.oauth2.SpotifyOAuth(scope=spotify_manager.scope, cache_handler=spotify_manager.cache_handler, show_dialog=True)
    
    # if request.GET.get("code"):
    #     auth_manager.get_cached_token(request.GET.get("code"))
    #     return redirect('/home')
    
    if not spotify_manager.auth_manager.validate_token(spotify_manager.cache_handler.get_cached_token()):
        auth_url = spotify_manager.auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign In</a></h2>'

    return spotify_manager

        