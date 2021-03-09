from django.shortcuts import render, redirect
from user_profile.forms import ExtendedUserCreationForm, UserProfileForm
from user_profile.models import UserProfile, Preferences, Settings, Playlist
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

# Create your views here.

def sign_up(request):
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
            # profile.settings_fk = sett
            #profile.following_fk = UserProfile.objects.none()
            #profile.playlists_followed_fk = Playlist.objects.none()
            #profile.settings_fk.user_profile_id = profile.id

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request, ('Successfully signed up!'))
            return redirect('/recommender/')

    else:
        form = ExtendedUserCreationForm()
        profile_form = UserProfileForm()
    return render(request, 'sign_up.html', {'form': form, 'profile_form': profile_form})

def logout_request(request):
    logout(request)
    messages.info(request, ('Logged out successfully!'))
    return redirect("/recommender/")


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"You are now logged in as {username}")
                return redirect('/recommender/')
            else:
                messages.error(request, ('Invalid username or password.'))
        else:
            messages.error(request, ('Invalid username or password.'))
    form = AuthenticationForm()
    return render(request, 'login.html', {"form":form})
