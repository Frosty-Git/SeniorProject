from django.shortcuts import render, redirect
from user_profile.models import *
from user_profile.forms import *
from social_feed.models import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.models import User
from django.utils import timezone

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
    Last updated: 3/8/21 by Marc Colin, Katie Lee, Jacelynn Duranceau, Kevin Magill
    """
    profile = UserProfile.objects.get(pk=user_id)
    post_list = Post.objects.filter(user_profile_fk=profile)
    follower_list = profile.users_followed.all()[:5]
    return render(request, 'profile/my_profile.html', {'profile': profile, 'post_list': post_list, 'follower_list': follower_list})


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
    Alters a user's settings.
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
    Used to display each user followed by a particular user. It uses said user as
    the primary key into the following bridging table and returns every foreign
    key, which represents the users followed.
    Last updated: 3/11/21 by Jacelynn Duranceau
    """
    you = UserProfile.objects.get(pk=user_id)
    following = you.users_followed.all()
    # following = FollowedUser.objects.filter(user_from=user_id)
    # get_list = FollowedUser.objects.get(user_from=user_id)
    #following = get_list.user_to
    return render(request, 'profile/following.html', {'following': following})

def unfollow(request, user_id, who):
    """
    Deletes the link in the bridging table between yourself and the person you
    want to unfollow.
    Last updated: 3/11/21 by Jacelynn Duranceau
    """
    user_to_unfollow = FollowedUser.objects.get(user_from = user_id, user_to = who)
    user_to_unfollow.delete()
    #who.followers -= 1
    url = '/user/following/' + user_id
    return redirect(url)

def follow(request, user_id, who):
    """
    Creates the link in the bridging table between yourself and the person you
    want to follow.
    Last updated: 3/17/21 by Katie Lee
    """
    loggedin = UserProfile.objects.get(pk=user_id)
    follower = UserProfile.objects.get(pk=who)
    user_to_follow = FollowedUser(user_from=loggedin, user_to=follower)
    user_to_follow.save()
    url = '/user/following/' + user_id
    return redirect(url)

def other_profile(request, user_id):
    """
    Used for profiles that are not the logged in user's profile.
    Last updated: 3/17/21 by Katie Lee
    """
    profile = UserProfile.objects.get(pk=user_id)
    follower = FollowedUser.objects.filter(user_from=request.user.id, user_to=user_id).first()
    is_following = False if follower is None else True
    return render(request, 'profile/other_profile.html', {'profile': profile, 'is_following': is_following})

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