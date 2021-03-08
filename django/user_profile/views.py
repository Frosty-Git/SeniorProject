from django.shortcuts import render
from user_profile.forms import ExtendedUserCreationForm, UserProfileForm
from user_profile.models import UserProfile, Preferences, Settings, Playlist

# Create your views here.
def sign_up(request):
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid() and profile_form.is_valid():
            user = form.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.preferences_fk = Preferences(accousticness=0.0, danceability=0.0, energy=0.0, instrumentalness=0.0, speechiness=0.0, loudness=0.0, tempo=0.0, valence=0.0)
            profile.settings_fk = Settings(user_profile_id=profile.id, private_profile=False, private_playlists=False, light_mode=False, explicit_music=False, live_music=False)
            # profile.following_fk = UserProfile()
            # profile.playlists_followed_fk = 

            profile.save()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request, ('Successfully signed up!'))
            return redirect('recommender/')

    else:
        form = ExtendedUserCreationForm()
        profile_form = UserProfileForm()
    return render(request, 'sign_up.html', {'form': form, 'profile_form': profile_form})