from django.shortcuts import render, redirect
from user_profile.models import *
from user_profile.forms import *
from social_feed.models import *
from social_feed.views import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.models import User
from django.utils import timezone
import json
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import recommender.Scripts.client_credentials as client_cred
from recommender.Scripts.spotify_manager import SpotifyManager

# Create your views here.

# global variable for spotify manager
spotify_manager = SpotifyManager()

def sign_up(request):
    """
    Allows a client to sign up as user for our site. Creates a user and a
    user profile for the client.
    Last updated: 3/16/21 by Marc Colin, Katie Lee, Jacelynn Duranceau, Kevin Magill
    """
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid() and profile_form.is_valid():
            user = form.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            pref = Preferences(user_profile_fk = profile)
            pref.save()
            sett = Settings(user_profile_fk = profile, private_profile=False, private_playlists=False, light_mode=False, explicit_music=False, live_music=False)
            sett.save()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request, ('Successfully signed up!'))
            return redirect('/')
    else:
        form = ExtendedUserCreationForm()
        profile_form = UserProfileForm()
    return render(request, 'registration/sign_up.html', {'form': form, 'profile_form': profile_form})

def logout_request(request):
    """
    Allows a user to logout from the site
    Last updated: 3/16/21 by Marc Colin, Katie Lee, Jacelynn Duranceau, Kevin Magill
    """
    logout(request)
    messages.info(request, ('Logged out successfully!'))
    return redirect("/")


def login_request(request):
    """
    Allows a user to log in to the site.
    Last updated: 3/16/21 by Marc Colin, Katie Lee, Jacelynn Duranceau, Kevin Magill
    """
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"You are now logged in as {username}")
                return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {"form": form})



def profile(request, user_id):
    """
    Used to display a user's information on their profile
    Last updated: 3/20/21 by Marc Colin, Katie Lee, Jacelynn Duranceau, Kevin Magill
    """
    all_prefs = get_preferences(user_id)
    if request.user == User.objects.get(pk=user_id):
        profile = UserProfile.objects.get(pk=user_id)
        posts = Post.objects.filter(user_profile_fk=profile).order_by('-date_last_updated')
        follower_list = profile.users_followed.all()[:5]
        votes = PostUserVote.objects.filter(user_from=profile).values()
        postform = PostForm()
        post_list = vote_dictionary(votes, posts)

        context = {
            'postform': postform,
            'profile': profile,
            'follower_list': follower_list,
            'post_list': post_list,
            'image': profile.profilepic,
            'acousticness': all_prefs['acousticness'],
            'danceability': all_prefs['danceability'],
            'energy': all_prefs['energy'],
            'instrumentalness': all_prefs['instrumentalness'],
            'speechiness': all_prefs['speechiness'],
            'loudness': all_prefs['loudness'],
            'loudness_adjusted': all_prefs['loudness_adjusted'],
            'tempo': all_prefs['tempo'],
            'valence': all_prefs['valence'],
            'private_prefs': all_prefs['private_prefs'],
        }
    else:
        if request.user.id is not None:
            loggedin = UserProfile.objects.get(pk=request.user.id)
            follower = FollowedUser.objects.filter(user_from=request.user.id, user_to=user_id).first()
            is_following = False if follower is None else True
            votes = PostUserVote.objects.filter(user_from=loggedin).values()
            profile = UserProfile.objects.get(pk=user_id)
            posts = Post.objects.filter(user_profile_fk=profile).order_by('-date_last_updated')
            follower_list = profile.users_followed.all()[:5]
            post_list = vote_dictionary(votes, posts)

            context = {
                'profile': profile,
                'post_list': post_list,
                'follower_list': follower_list,
                'is_following': is_following,
                'image': loggedin.profilepic,
                'acousticness': all_prefs['acousticness'],
                'danceability': all_prefs['danceability'],
                'energy': all_prefs['energy'],
                'instrumentalness': all_prefs['instrumentalness'],
                'speechiness': all_prefs['speechiness'],
                'loudness': all_prefs['loudness'],
                'loudness_adjusted': all_prefs['loudness_adjusted'],
                'tempo': all_prefs['tempo'],
                'valence': all_prefs['valence'],
                'private_prefs': all_prefs['private_prefs'],
            }
        else:
            profile = UserProfile.objects.get(pk=user_id)
            posts = Post.objects.filter(user_profile_fk=profile).order_by('-date_last_updated')
            follower_list = profile.users_followed.all()[:5]

            nli_post_list = []
            for post in posts:
                new_post = cast_subclass(post)
                nli_post_list.append(new_post)

            context = {
                'profile': profile,
                'nli_post_list': nli_post_list,
                'follower_list': follower_list,
                'nofollow': 'nofollow',
                'acousticness': all_prefs['acousticness'],
                'danceability': all_prefs['danceability'],
                'energy': all_prefs['energy'],
                'instrumentalness': all_prefs['instrumentalness'],
                'speechiness': all_prefs['speechiness'],
                'loudness': all_prefs['loudness'],
                'loudness_adjusted': all_prefs['loudness_adjusted'],
                'tempo': all_prefs['tempo'],
                'valence': all_prefs['valence'],
                'private_prefs': all_prefs['private_prefs'],
            }
    return render(request, 'profile/profile.html', context)

def vote_dictionary(votes, posts):
    """
    Creates a dictionary that makes the post the key
    and upvote/downvote in a list the value.
    Last updated: 3/30/21 by Katie Lee
    """
    post_list = {}
    for post in posts:
        new_post = cast_subclass(post)
        up = False
        down = False
        for vote in votes:
            if vote.get('post_to_id') == post.id:
                if vote.get('vote') == 'Like':
                    up = True
                elif vote.get('vote') == 'Dislike':
                    down = True
        post_list[new_post] = [up, down]
    return post_list


@require_GET
def display_settings(request, user_id):
    """
    Used to display the settings for a particular user. Loads in the current state
    of each field from the database.
    Last updated: 3/11/21 by Jacelynn Duranceau
    """
    userobj = User.objects.get(id=user_id)
    settings = Settings.objects.get(user_profile_fk=user_id)
    settings_form = SettingsForm(instance=settings)
    return render(request, 'settings/settings.html', {'settings_form': settings_form, 'userobj': userobj})

@require_POST
def settings_save(request, user_id):
    """
    Alteers a user's settings.
    Last updated: 3/11/21 by Jacelynn Duranceau 
    """
    setting = Settings.objects.get(user_profile_fk=user_id)
    settings_form = SettingsForm(request.POST, instance=setting)
    if settings_form.is_valid():
        setting.private_profile = settings_form.cleaned_data.get('private_profile')
        setting.private_playlists = settings_form.cleaned_data.get('private_playlists')
        setting.private_preferences = settings_form.cleaned_data.get('private_preferences')
        setting.light_mode = settings_form.cleaned_data.get('light_mode')
        setting.explicit_music = settings_form.cleaned_data.get('explicit_music')
        setting.live_music = settings_form.cleaned_data.get('live_music')
        setting.save()
        messages.success(request, ('Settings have been updated!'))
        url = '/user/settings/' + user_id
        return redirect(url)
    else:
        raise Http404('Form not valid')

@require_GET
def display_following(request, user_id):
    """
    Used to display each user a particular user follows. It uses said user
    as the primary key into the following bridging table and returns every
    foreign key, which represents the users followed.
    Last updated: 3/11/21 by Jacelynn Duranceau
    """
    you = UserProfile.objects.get(pk=user_id)
    following = you.users_followed.all()
    # following = FollowedUser.objects.filter(user_from=user_id)
    # get_list = FollowedUser.objects.get(user_from=user_id)
    #following = get_list.user_to
    return render(request, 'profile/following.html', {'following': following})

@require_GET
def display_followers(request, user_id):
    """
    Used to display the followers of a particular user. It uses said user as
    the primary key into the following bridging table and returns every user
    that is the user_from match in said table.
    Last updated: 3/11/21 by Jacelynn Duranceau
    """
    user = UserProfile.objects.get(pk=user_id)
    follower_ids = FollowedUser.objects.filter(user_to=user).values('user_from') # Returns dictionary of ids
    followers = []
    for user in follower_ids:
        for id in user.values():
            followers.append(UserProfile.objects.get(pk=id))
    return render(request, 'profile/followers.html', {'followers': followers})

def unfollow(request, user_id, who):
    """
    Deletes the link in the bridging table between yourself and the person you
    want to unfollow.
    Last updated: 3/19/21 by Jacelynn Duranceau
    """
    loggedin = UserProfile.objects.get(pk=user_id)
    loggedin.num_following -= 1
    loggedin.save()
    to_unfollow = UserProfile.objects.get(pk=who)
    to_unfollow.num_followers -= 1
    to_unfollow.save()
    user_to_unfollow = FollowedUser.objects.get(user_from = user_id, user_to = who)
    user_to_unfollow.delete()
    url = '/user/following/' + user_id
    return redirect(url)

def follow(request, user_id, who):
    """
    Creates the link in the bridging table between yourself and the person you
    want to follow.
    Last updated: 3/19/21 by Katie Lee, Jacelynn Duranceau
    """
    loggedin = UserProfile.objects.get(pk=user_id)
    loggedin.num_following += 1
    loggedin.save()
    to_follow = UserProfile.objects.get(pk=who)
    to_follow.num_followers += 1
    to_follow.save()
    user_to_follow = FollowedUser(user_from=loggedin, user_to=to_follow)
    user_to_follow.save()
    url = '/user/following/' + user_id
    return redirect(url)


# def num_followers(user_id):
#     followers = FollowedUser.objects.get(user_to = user_id).len()
#     return {'followers': followers}

@login_required
def update_profile(request):
    """
    Used to make a change to what is currently displayed on a user's profile.
    Note: These attributes are initially set upon signing up.   
    Last updated: 3/8/21 by Marc Colin, Katie Lee, Jacelynn Duranceau, Kevin Magill
    """
    obj = UserProfile.objects.get(pk=request.user.id)

    if request.method == 'POST':
        form = ExtendedUserChangeForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if form.is_valid() and profile_form.is_valid():
            user = form.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.date_last_update = timezone.now()
            
            profile.save()
            messages.success(request, ('Profile has been updated!'))
            return redirect('/user/update_profile/')
    else:
        form = ExtendedUserChangeForm(instance=obj.user)
        profile_form = UserProfileForm(instance=obj)
    return render(request, 'settings/update_profile.html', {'form': form, 'profile_form': profile_form})

def user_list(request):
    """
    TEMPORARY just to see what users are in the system 
    """
    user_list = UserProfile.objects.exclude(pk=request.user.id)
    return render(request, 'profile/user_list.html', {'user_list': user_list})

def get_playlists(request, user_id):
    """
    Gets all playlists for yourself.
    Last updated: 3/23/21 by Joe Frost, Jacelynn Duranceau, Tucker Elliott
    """
    # Check to see you are accessing the playlist page that is your own.
    if request.user == User.objects.get(pk=user_id):
        you = UserProfile.objects.get(pk=user_id)
        playlists = Playlist.objects.filter(user_profile_fk=you)
        playlistform = PlaylistForm()
        context = {
            'playlists': playlists,
            'playlistform': playlistform,
            'profile': you,
        }
        return render(request, 'playlists/playlists.html', context)
    # If it is not your own, then redirect to the page set up for viewing
    # playlists that aren't yours.
    else:
        return redirect('/user/otherplaylists/' + str(user_id))

def other_playlists(request, user_id):
    """
    Gets all playlists for a user.
    Last updated: 3/23/27 by Jacelynn Duranceau
    """
    # There would be no reason to be able to access the playlist page where you
    # wouldn't be able to edit it if it is your own, so we check that you are
    # accessing one that isn't.
    if request.user != User.objects.get(pk=user_id):
        user = UserProfile.objects.get(pk=user_id)
        all_playlists = Playlist.objects.filter(user_profile_fk=user)
        playlists = []
        # Only show playlists that aren't private
        for playlist in all_playlists:
            if playlist.is_private is False:
                playlists.append(playlist)
        context = {
            'playlists': playlists,
            'profile': user,
        }
        return render(request, 'playlists/other_playlists.html', context)
    # If the playlist is yours, then redirect to the page where you can actually
    # modify it.
    else:
        return redirect('/user/playlists/' + str(user_id))

def get_songs_playlist(request, playlist_id):
    """
    Gets the songs on your playlist based on the playlist's id
    Last updated: 3/28/21 by Jacelynn Duranceau, Tucker Elliot, Joe Frost
    """
    you = UserProfile.objects.get(pk=request.user.id)
    # This automatically makes it so that you can't access a playlist that is
    # not yours since there will be no matching playlist query for your user id
    # if the playlist actually belongs to another user. It will go through the
    # exception block if so.
    try:
        playlist = Playlist.objects.get(pk=playlist_id, user_profile_fk=you)
        matches = SongOnPlaylist.objects.filter(playlist_from=playlist).values()
        songs = {}
        for match in matches:
            # sop_id is the id for the primary key of the row into the SongOnPlaylist
            # table that the matching songs to playlists come from
            sop_id = match.get('id')
            song_id = match.get('spotify_id')
            songs[sop_id] = song_id

        context = {
            'songs': songs,
            'playlist': playlist,
        }
        return render(request, 'playlists/single_playlist.html', context)
    except:
        # Redirect back to your own playlists page if you are trying to access
        # a playlist that does not belong to you or does not exist.
        return redirect('/user/playlists/' + str(request.user.id))

def get_other_songs_playlist(request, user_id, playlist_id):
    """
    Gets the songs on a user's playlist based on the playlist's id
    Last updated: 3/28/21 by Jacelynn Duranceau
    """
    # Checks to see the playlist page you are accessing isn't your own
    if request.user != User.objects.get(pk=user_id): 
        user = UserProfile.objects.get(pk=user_id)
        playlist = Playlist.objects.get(pk=playlist_id, user_profile_fk=user)
        # Do not allow access to a user's private playlist
        if playlist.is_private:
            return redirect('/user/playlists/' + str(user_id))
        matches = SongOnPlaylist.objects.filter(playlist_from=playlist).values()
        songs = {}
        for match in matches:
            # sop_id is the id for the primary key of the row into the SongOnPlaylist
            # table that the matching songs to playlists come from
            sop_id = match.get('id')
            song_id = match.get('spotify_id')
            songs[sop_id] = song_id

        context = {
            'songs': songs,
            'playlist': playlist,
            'profile': user,
        }
        return render(request, 'playlists/other_single_playlist.html', context)
    else:
        # This means you are trying to access your own playlist page, so redirect
        # there.
        return redirect('/user/playlist/' + str(playlist_id))

def create_playlist_popup(request):
    """
    Creates a playlist
    Last updated: 3/24/21 by Joe Frost, Jacelynn Duranceau, Tucker Elliot
    """
    if request.method == 'POST':
        playlist_form = PlaylistForm(request.POST, request.FILES)
        if playlist_form.is_valid():
            you = UserProfile.objects.get(pk=request.user.id)
            playlist = Playlist(user_profile_fk=you, name=playlist_form.cleaned_data.get('name'), 
                                image=playlist_form.cleaned_data.get('image'),
                                is_private=playlist_form.cleaned_data.get('is_private'))
            playlist.save()
            # playlist = playlist_form.save(commit=False)
            return redirect('/user/playlists/' + str(request.user.id))    #redirect to the playlist

def add_song_to_playlist(request, query):
    """
    Adds a song to a playlist
    Last updated: 3/24/21 by Jacelynn Duranceau
    """
    if request.method == 'POST':
        # user_id = request.user.id
        # user = UserProfile.objects.get(pk=user_id)
        track_term = request.POST.get('track_id')
        song = SongId.objects.get(pk=track_term)
        playlist_id = request.POST.get('playlist_id')
        playlist = Playlist.objects.get(pk=playlist_id)
        new_song = SongOnPlaylist(playlist_from=playlist, spotify_id=song)
        new_song.save()
        return redirect('/')
        # return redirect('/results/')
        #return redirect('/user/playlists/' + str(request.user.id))
        # return render(request, 'recommender/results.html')
    else:
        return render(request, 'playlists/addsong_popup.html')

def edit_playlist_popup(request):
    """
    Updates a user's playlist
    Last updated: 3/27/21 by Jacelynn Duranceau
    """
    if request.method == 'POST':
        playlist_id = request.POST.get('playlist_id')
        playlist = Playlist.objects.get(pk=playlist_id)
        name = request.POST.get('new_name')
        img = request.FILES.get('img')
        if playlist.is_private is True:
            is_private = request.POST.get('is_private_t')
        elif playlist.is_private is False:
            is_private = request.POST.get('is_private_f')
        if is_private == 'on':
            is_private = True
        elif is_private == None:
            is_private = False
        if name is not None:
            playlist.name = name
            if img is not None:
                playlist.image = img
            playlist.is_private = is_private
            playlist.date_last_updated = timezone.now()
            playlist.save()
        return redirect('/user/playlist/' + str(playlist_id))
    else:
        return render(request, 'playlists/editplaylist_popup.html')

def delete_playlist(request, playlist_id):
    """
    Deletes a user's playlist.
    Last updated: 3/24/21 by Jacelynn Duranceau
    """
    playlist = Playlist.objects.get(pk=playlist_id)
    playlist.delete()
    return redirect('/user/playlists/' + str(request.user.id))

def delete_song(request, playlist_id, sop_pk):
    """
    Deletes a song on a user's playlist. Takes into account duplicates, so it
    will not delete every instance of the song you're deleting.
    Last updated: 3/24/21 by Jacelynn Duranceau
    """
    # sop_pk is the primary key into the row of the SongOnPlaylist object that
    # the match comes from
    song = SongOnPlaylist.objects.get(pk=sop_pk)
    song.delete()
    return redirect('/user/playlist/' + str(playlist_id))

def link_spotify(request):
    spotify = spotify_manager.create_spotify()
    spotify.me()
    return redirect()

def save_token_redirect(request):
    spotify = spotify_manager.create_spotify()
    cached_token = spotify_manager.auth_manager.get_cached_token()
    if(int(request.user.id) == int(request.session.get('_auth_user_id'))):
        user = UserProfile.objects.get(user=request.user.id)
        user.access_token = cached_token['access_token']
        user.refresh_token = cached_token['refresh_token']
        user.expires_at = cached_token['expires_at']
        user.scope = cached_token['scope']
        user.linked_to_spotify = True
        user.save()
    return redirect('/')

def get_preferences(user_id):
    """
    Gets the preferences for a user.
    Last updated: 3/30/21 by Jacelynn Duranceau
    """
    user = UserProfile.objects.get(pk=user_id)
    settings = Settings.objects.get(user_profile_fk=user)
    private_prefs = settings.private_preferences
    prefs = Preferences.objects.get(user_profile_fk=user)
    acousticness = prefs.acousticness
    danceability = prefs.danceability
    energy = prefs.energy
    instrumentalness = prefs.instrumentalness
    speechiness = prefs.speechiness
    loudness = prefs.loudness
    # This value is negative and cannot be shown properly on the template 
    # in a progress bar unless adjusted to be a positive. So, for the progress bar
    # purposes the range will be 0 to 60 rather than -60 to 0
    loudness_adjusted = loudness + 60
    tempo = prefs.tempo
    valence = prefs.valence
    user_prefs = {
        'private_prefs': private_prefs,
        'acousticness': acousticness,
        'danceability': danceability,
        'energy': energy,
        'instrumentalness': instrumentalness,
        'speechiness': speechiness,
        'loudness': loudness,
        'loudness_adjusted': loudness_adjusted,
        'tempo': tempo,
        'valence': valence,
    }
    return user_prefs

def reset_prefs(request):
    """
    Reset the user's preferences back to the default value
    """
    

