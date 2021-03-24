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

# Create your views here.

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
            pref = Preferences(user_profile_fk = profile, accousticness=0.0, danceability=0.0, energy=0.0, instrumentalness=0.0, speechiness=0.0, loudness=0.0, tempo=0.0, valence=0.0)
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


@login_required
def profile(request, user_id):
    """
    Used to display a user's information on their profile
    Last updated: 3/20/21 by Marc Colin, Katie Lee, Jacelynn Duranceau, Kevin Magill
    """
    if request.user == User.objects.get(pk=user_id):
        profile = UserProfile.objects.get(pk=user_id)
        posts = Post.objects.filter(user_profile_fk=profile).order_by('-date_last_updated')
        follower_list = profile.users_followed.all()[:5]
        postform = PostForm()
        post_list = []
        
        for post in posts:
            new_post = cast_subclass(post)
            post_list.append(new_post)
        
        context = {
            'postform': postform,
            'profile': profile,
            'post_list': post_list,
            'follower_list': follower_list
        }
        return render(request, 'profile/my_profile.html', context)
    else:
        return redirect('/user/userprofile/' + str(user_id))


def other_profile(request, user_id):
    """
    Used for profiles that are not the logged in user's profile.
    Last updated: 3/20/21 by Katie Lee
    """
    if request.user != User.objects.get(pk=user_id):
        profile = UserProfile.objects.get(pk=user_id)
        follower = FollowedUser.objects.filter(user_from=request.user.id, user_to=user_id).first()
        is_following = False if follower is None else True
        post_list = Post.objects.filter(user_profile_fk=profile).order_by('-date_last_updated')
        follower_list = profile.users_followed.all()[:5]
        context = {
            'profile': profile,
            'post_list': post_list,
            'follower_list': follower_list,
            'is_following': is_following,
        }
        return render(request, 'profile/other_profile.html', context)
    else:
        return redirect('/user/profile/' + str(user_id))


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
