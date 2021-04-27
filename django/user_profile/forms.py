from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.forms import ModelForm
import datetime
from user_profile.models import *


class ExtendedUserCreationForm(UserCreationForm):
    """
    Using the existing Django UserCreationForm, this
    will take in an email, first and last name to create
    the Django User used as a pk for UserProfile.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ( 'username', 'first_name', 'last_name', 'email', 'password1', 'password2',)


    def save(self, commit=True):
        """
        Saves the written fields in the form to the User object.
        """
        user = super().save(commit=False)
        
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
        
        return user


class UserProfileForm(forms.ModelForm):
    """
    Form for the extraneous fields not included in Django User.
    """
    profilepic = forms.ImageField(required=False)
    description = forms.CharField(widget=forms.Textarea, required=False, max_length=100)
    likes = forms.CharField(widget=forms.Textarea, required=False, max_length=50)
    dislikes = forms.CharField(widget=forms.Textarea, required=False, max_length=50)

    class Meta:
        model = UserProfile
        fields = ('description', 'likes', 'dislikes', 'profilepic')


class SettingsForm(forms.ModelForm):
    """
    Form for changing your settings. The settings include making your profile
    private, making your preferences for song features private, and making
    it so that you receive recommendations for explicit songs.
    """
    class Meta:
        model = Settings
        widgets = {'private_profile': forms.CheckboxInput(attrs={'id': 'i_private_profile'})}
        fields = ['private_profile', 'private_preferences', 'explicit_music']


class ExtendedUserChangeForm(UserChangeForm):
    """
    To update the Django User fields, UserChangeForm is inherited.
    It will change the fields for the pk User object for UserProfile.
    """
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    password = None

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)

class PlaylistForm(forms.ModelForm):
    """
    Form to create a new playlist.
    """
    name = forms.CharField(max_length=30)
    image = forms.ImageField(required=False)
    description = forms.CharField(widget=forms.Textarea, required=True, max_length=299)
    date_created = datetime.datetime.now()
    is_private = forms.BooleanField(required=False)
    is_shareable = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Playlist
        fields = ('name', 'image', 'is_private', 'is_shareable')

    def __init__(self, *args, **kwargs):
        """
        Customizes the display of widgets in the create playlist popup.
        """
        super(PlaylistForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['style'] = 'width: 100%; height: 1.75rem; overflow: hidden; border-radius: 0.3rem; border: none'
        self.fields['name'].widget.attrs['style'] = 'width: 100%; height: 1.75rem; border-radius: 0.3rem; border: none'
        self.fields['image'].widget.attrs['style'] = 'width: 50%'
        self.fields['is_shareable'].widget.attrs['class'] = 'form-check-input playlistPop'
        self.fields['is_private'].widget.attrs['class'] = 'form-check-input playlistPop'


