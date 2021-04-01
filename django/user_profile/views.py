
from django.shortcuts import render, redirect
from requests.sessions import Session
from user_profile.models import *
from user_profile.forms import *
from social_feed.models import *
from social_feed.views import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils.safestring import mark_safe
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
import os
from django.core.cache import cache

# Create your views here.

# global variables for spotify manager
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
            liked_songs = Playlist(user_profile_fk=profile, name="My Liked Songs")
            liked_songs.save()
            profile.liked_songs_playlist_fk = liked_songs
            profile.save()

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
        is_profile_private = profile_privacy(user_id)

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
            'tempo_adjusted': all_prefs['tempo_adjusted'],
            'valence': all_prefs['valence'],
            'private_prefs': all_prefs['private_prefs'],
            'private_profile': is_profile_private,
        }
    else:
        if request.user.id is not None:
            loggedin = UserProfile.objects.get(pk=request.user.id)
            follower = FollowedUser.objects.filter(user_from=request.user.id, user_to=user_id).first()
            bool_following = False if follower is None else True
            votes = PostUserVote.objects.filter(user_from=loggedin).values()
            profile = UserProfile.objects.get(pk=user_id)
            posts = Post.objects.filter(user_profile_fk=profile).order_by('-date_last_updated')
            follower_list = profile.users_followed.all()[:5]
            post_list = vote_dictionary(votes, posts)
            is_profile_private = profile_privacy(user_id)
            following_status = is_following(request.user.id, user_id)

            context = {
                'profile': profile,
                'post_list': post_list,
                'follower_list': follower_list,
                'is_following': bool_following,
                'image': loggedin.profilepic,
                'acousticness': all_prefs['acousticness']*100,
                'danceability': all_prefs['danceability'],
                'energy': all_prefs['energy'],
                'instrumentalness': all_prefs['instrumentalness'],
                'speechiness': all_prefs['speechiness'],
                'loudness': all_prefs['loudness'],
                'loudness_adjusted': all_prefs['loudness_adjusted'],
                'tempo': all_prefs['tempo'],
                'tempo_adjusted': all_prefs['tempo_adjusted'],
                'valence': all_prefs['valence'],
                'private_prefs': all_prefs['private_prefs'],
                'private_profile': is_profile_private,
            }
        else:
            profile = UserProfile.objects.get(pk=user_id)
            posts = Post.objects.filter(user_profile_fk=profile).order_by('-date_last_updated')
            follower_list = profile.users_followed.all()[:5]
            is_profile_private = profile_privacy(user_id)

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
                'tempo_adjusted': all_prefs['tempo_adjusted'],
                'valence': all_prefs['valence'],
                'private_prefs': all_prefs['private_prefs'],
                'private_profile': is_profile_private,
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
    if request.user == User.objects.get(pk=user_id):
        you = UserProfile.objects.get(pk=user_id)
        following = you.users_followed.all()
        following_arr = []
        for user_profile in following:
            determination = is_following(request.user.id, user_profile.user.id)
            #following_dict[user_profile].append(determination)
            following_arr.append([user_profile, determination])
        # following = FollowedUser.objects.filter(user_from=user_id)
        # get_list = FollowedUser.objects.get(user_from=user_id)
        #following = get_list.user_to
        context = {
            'profile': you,
            'following': following_arr,
        }
        return render(request, 'profile/following.html', context)
    else:
        other_user = UserProfile.objects.get(pk=user_id)
        private_profile = profile_privacy(user_id)
        following_status = is_following(request.user.id, other_user.user.id)
        if following_status or not private_profile:
            following = other_user.users_followed.all()
            following_arr = []
            for user_profile in following:
                determination = is_following(request.user.id, user_profile.user.id)
                #following_dict[user_profile].append(determination)
                following_arr.append([user_profile, determination])
            # following = FollowedUser.objects.filter(user_from=user_id)
            # get_list = FollowedUser.objects.get(user_from=user_id)
            #following = get_list.user_to
            context = {
                'following': following_arr,
                'profile': other_user,
                'private_profile': private_profile,
                'following_status': following_status,
            }
            return render(request, 'profile/following.html', context)
        else:
            return redirect('/user/following/' + str(request.user.id))

@require_GET
def display_followers(request, user_id):
    """
    Used to display the followers of a particular user. It uses said user as
    the primary key into the following bridging table and returns every user
    that is the user_from match in said table.
    Last updated: 3/11/21 by Jacelynn Duranceau
    """
    if request.user == User.objects.get(pk=user_id):
        you = UserProfile.objects.get(pk=user_id)
        follower_ids = FollowedUser.objects.filter(user_to=you).values('user_from') # Returns dictionary of ids
        followers_arr = []
        for user in follower_ids:
            for id in user.values():
                person = UserProfile.objects.get(pk=id)
                determination = is_following(request.user.id, id)
                followers_arr.append([person, determination])
        context = {
            'profile': you,
            'followers': followers_arr,
        }
        return render(request, 'profile/followers.html', context)
    else:
        other_user = UserProfile.objects.get(pk=user_id)
        private_profile = profile_privacy(user_id)
        following_status = is_following(request.user.id, other_user.user.id)
        if following_status or not private_profile:
            follower_ids = FollowedUser.objects.filter(user_to=other_user).values('user_from') # Returns dictionary of ids
            followers_arr = []
            for user in follower_ids:
                for id in user.values():
                    person = UserProfile.objects.get(pk=id)
                    determination = is_following(request.user.id, id)
                    followers_arr.append([person, determination])
            context = {
                'profile': other_user,
                'followers': followers_arr,
            }
            return render(request, 'profile/followers.html', context)
        else:
            return redirect('/user/followers/' + str(request.user.id))

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
    Gets all playlists for a user.
    Last updated: 3/31/21 by Jacelynn Duranceau, Tucker Elliott, Joe Frost
    """
    # Check to see you are accessing the playlist page that is your own.
    if request.user == User.objects.get(pk=user_id):
        you = UserProfile.objects.get(pk=request.user.id)
        playlists = Playlist.objects.filter(user_profile_fk=you)
        playlistform = PlaylistForm()
        private_profile = profile_privacy(user_id)
        following_status = is_following(request.user.id, user_id)
        context = {
            'playlists': playlists,
            'playlistform': playlistform,
            'profile': you,
            'private_profile': private_profile,
            'following_status': following_status,
        }
        return render(request, 'playlists/playlists.html', context)
    else:
        other_user = UserProfile.objects.get(pk=user_id)
        private_profile = profile_privacy(user_id)
        following_status = is_following(request.user.id, other_user.user.id)
        # following_status or 
        if following_status or not private_profile:
            playlists = Playlist.objects.filter(user_profile_fk=other_user)
            context = {
                'playlists': playlists,
                'profile': other_user,
                'private_profile': private_profile,
                'following_status': following_status,
            }
            return render(request, 'playlists/playlists.html', context)
        else:
            # Redirect back to your own playlist page since the user is private
            # and you don't follow them
            return redirect('/user/playlists/' + str(request.user.id))

def get_songs_playlist(request, user_id, playlist_id):
    """
    Gets the songs on your playlist based on the playlist's id
    Last updated: 3/28/21 by Jacelynn Duranceau, Tucker Elliot, Joseph Frost
    """
    if request.user == User.objects.get(pk=user_id):
        you = UserProfile.objects.get(pk=request.user.id)
        playlist = Playlist.objects.get(pk=playlist_id, user_profile_fk=you)
        matches = SongOnPlaylist.objects.filter(playlist_from=playlist).values()
        songs = {}
        for match in matches:
            # sop_id is the id for the primary key of the row into the SongOnPlaylist
            # table that the matching songs to playlists come from
            sop_id = match.get('id')
            # The result appends 'id' to our original name of 'spotify_id', hence the extra 'id' in the name
            song_id = match.get('spotify_id_id')
            songs[sop_id] = song_id
        
        private_profile = profile_privacy(user_id)
        following_status = is_following(request.user.id, user_id)

        context = {
            'songs': songs,
            'playlist': playlist,
            'profile': you,
            'private_profile': private_profile,
            'following_status': following_status,
        }
        return render(request, 'playlists/single_playlist.html', context)
    else:
        other_user = UserProfile.objects.get(pk=user_id)
        private_profile = profile_privacy(user_id)
        following_status = is_following(request.user.id, other_user.user.id)
        # If the person's profile is not private or if you follow them, then you can
        # see their playlists
        if not private_profile or following_status:
            playlist = Playlist.objects.get(pk=playlist_id, user_profile_fk=other_user)
            if not playlist.is_private:
                matches = SongOnPlaylist.objects.filter(playlist_from=playlist).values()
                songs = {}
                for match in matches:
                    # sop_id is the id for the primary key of the row into the SongOnPlaylist
                    # table that the matching songs to playlists come from
                    sop_id = match.get('id')
                    # The result appends 'id' to our original name of 'spotify_id', hence the extra 'id' in the name
                    song_id = match.get('spotify_id_id')
                    songs[sop_id] = song_id

                context = {
                    'songs': songs,
                    'playlist': playlist,
                    'profile': other_user,
                    'private_profile': private_profile,
                    'following_status': following_status,
                }
                return render(request, 'playlists/single_playlist.html', context)
            else:
                # The single playlist you are trying to access is private, so redirect back to that 
                # user's playlists page
                return redirect('/user/playlists/' + str(user_id))
        else:
            # Redirect back to your own playlist page since the user is private
            return redirect('/user/playlists/' + str(request.user.id))

def create_playlist_popup(request):
    """
    Creates a playlist
    Last updated: 3/24/21 by Joe Frost, Jacelynn Duranceau, Tucker Elliott
    """
    if request.method == 'POST':
        playlist_form = PlaylistForm(request.POST, request.FILES)
        if playlist_form.is_valid():
            you = UserProfile.objects.get(pk=request.user.id)
            playlist = Playlist(user_profile_fk=you,
                                name=playlist_form.cleaned_data.get('name'), 
                                image=playlist_form.cleaned_data.get('image'),
                                is_private=playlist_form.cleaned_data.get('is_private'),
                                is_shareable=playlist_form.cleaned_data.get('is_shareable'))
                                description=playlist_form.cleaned_data.get('description')
                                )
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
    Last updated: 3/31/21 by Jacelynn Duranceau, Joe Frost, Tucker Elliott
    """
    if request.method == 'POST':
        playlist_id = request.POST.get('playlist_id')
        playlist = Playlist.objects.get(pk=playlist_id)
        name = request.POST.get('new_name')
        description = request.POST.get('new_description')
        img = request.FILES.get('img')

        if playlist.is_private is True:
            is_private = request.POST.get('is_private_t')
        elif playlist.is_private is False:
            is_private = request.POST.get('is_private_f')
        if is_private == 'on':
            is_private = True
        elif is_private == None:
            is_private = False

        if playlist.is_shareable is True:
            is_shareable = request.POST.get('is_shareable_t')
        elif playlist.is_shareable is False:
            is_shareable = request.POST.get('is_shareable_f')
        if is_shareable == 'on':
            is_shareable = True
        elif is_shareable == None:
            is_shareable = False
        
        if name is not None:
            playlist.name = name
            if img is not None:
                playlist.image = img
            if description is not None:
                playlist.description = description
            playlist.is_private = is_private
            playlist.is_shareable = is_shareable
            playlist.date_last_updated = timezone.now()
            playlist.save()
        return redirect('/user/playlist/' + str(request.user.id) +'/' + str(playlist_id))
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

def export_to_spotify(request, playlist_id):
    """
    Exports a playlist to the user's linked Spotify account. The exported 
    playlist will show up on that user's Spotify playlists list if they check 
    their Spotify app.
    Last updated: 3/31/2021 Joe Frost, Tucker Elliott
    """
    user = UserProfile.objects.get(pk=request.user.id)
    spotify_manager.token_check(request)
    spotify = spotipy.Spotify(auth=user.access_token)
    playlist = Playlist.objects.get(pk=playlist_id)
    # Check if the playlist is on Spotify already.
    if playlist.is_imported:
    # If it is already on Spotify, replace the playlist on Spotify with this new version.
        matches = SongOnPlaylist.objects.filter(playlist_from=playlist).values()
        song_ids = []
        for match in matches:
            song_ids.append(match.get('spotify_id'))
        spotify.playlist_replace_items(playlist.spotify_playlist_id, song_ids)
    else:
    # If it is not on Spotify, create the new playlist there, change our db boolean value
    # to say it is on Spotify, and get the Spotify playlist id saved into our db.
        spotify.user_playlist_create(user=user.spotify_user_id,
                                    name=playlist.name,
                                    public=(not playlist.is_private),
                                    collaborative=False,
                                    description=playlist.description)
        playlist.is_imported = True
        new_playlist_id = spotify.user_playlists(user.spotify_user_id, limit=1, offset=0).get('id')
        playlist.spotify_playlist_id = new_playlist_id
        playlist.save()
        print(new_playlist_id)
    return redirect('/user/playlists/' + str(request.user.id))

def link_spotify(request):
    """
    This is the on action method for the Link Spotify button in the 
    user profile page. It will send the user to the Spotify login page 
    if they are currently not logged in.
    Last updated: 3/31/2021 Joe Frost, Tucker Elliott
    """
    spotify = spotify_manager.create_spotify()
    spotify.me()
    return redirect('/')

def save_token_redirect(request):
    """
    This is a complementary view to the link_spotify view. After the user 
    logs into Spotify on the Spotify login page which they were sent to 
    after clicking the link spotify button in the user profile, the Spotify 
    page will send them here. This view saves the Spotify token data into our 
    database under the PengBeats user's profile entry.
    Last updated: 3/31/2021 Joe Frost, Tucker Elliott
    """
    spotify = spotify_manager.create_spotify()
    cached_token = spotify_manager.auth_manager.get_access_token(request.GET.__getitem__('code'))
    if(int(request.user.id) == int(request.session.get('_auth_user_id'))):
        user = UserProfile.objects.get(user=request.user.id)
        user.spotify_user_id = spotify.me().get('id')
        user.access_token = cached_token['access_token']
        user.refresh_token = cached_token['refresh_token']
        user.expires_at = cached_token['expires_at']
        user.scope = cached_token['scope']
        user.linked_to_spotify = True
        user.save()
        os.remove(os.path.abspath(".cache"))
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
    tempo_adjusted = tempo - 50
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
        'tempo_adjusted': tempo_adjusted,
        'valence': valence,
    }
    return user_prefs

def reset_preferences(request):
    """
    Reset the user's preferences back to the default value
    Last updated: 3/31/21 by Jacelynn Duranceau
    """
    user = UserProfile.objects.get(pk=request.user.id)
    prefs = Preferences.objects.get(user_profile_fk=user)
    prefs.acousticness = 0.5
    prefs.danceability = 0.5
    prefs.energy = 0.5
    prefs.instrumentalness = 0.5
    prefs.speechiness = 0.5
    prefs.loudness = -30
    prefs.tempo = 100
    prefs.valence = 0.5
    prefs.save()
    messages.success(request, mark_safe(f"Successfully reset all preferences! Retake the survey here: <a href='http://127.0.0.1:8000/survey/'>Survey</a>."))
    # return redirect('/survey/')
    return redirect('/user/update_profile/#/')

def delete_account(request):
    """
    Deletes a user's account. Updates the follower count of any individual you
    were following (-1). Updates the following count of any individual that was
    following you (-1).
    Last updated: 3/31/21 by Jacelynn Duranceau
    """
    your_profile = UserProfile.objects.get(pk=request.user.id)

    users_you_follow = your_profile.users_followed.all()
    for person in users_you_follow:
        person.num_followers -= 1
        person.save()

    users_following_you_ids = FollowedUser.objects.filter(user_to=your_profile).values('user_from')
    for result in users_following_you_ids:
        for id in result.values():
            person = UserProfile.objects.get(pk=id)
            person.num_following -= 1
            person.save()

    user = User.objects.get(pk=request.user.id)
    user.delete()
    messages.success(request, ('Account deletion successful!'))
    return redirect('/')

def is_following(your_id, user_to_id):
    """
    Determines where or not you follow a particular user.
    Last updated: 3/31/21 by Jacelynn Duranceau
    """
    you = UserProfile.objects.get(pk=your_id)
    is_following = False
    users_you_follow = you.users_followed.all()
    for person in users_you_follow:
        if person.user.id == user_to_id:
            is_following = True
            break
    # users_you_follow = FollowedUser.objects.filter(user_from=you).values('user_to')
    # for result in users_you_follow:
    #     for id in result.values():
    #         if id == user_to_id:
    #             is_following = True
    #             break
    
    return is_following
        
def profile_privacy(user_id):
    """
    Tells you whether or not a user has set their profile to private
    Last updated: 3/31/21 by Jacelynn Duranceau
    """
    user = UserProfile.objects.get(pk=user_id)
    settings = Settings.objects.get(user_profile_fk=user)
    profile_privacy = settings.private_profile
    return profile_privacy