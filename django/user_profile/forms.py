from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from user_profile.models import *
from django.forms import ModelForm
import datetime


class ExtendedUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ( 'username', 'first_name', 'last_name', 'email', 'password1', 'password2',)


    def save(self, commit=True):
        user = super().save(commit=False)
        
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
        
        return user


class UserProfileForm(forms.ModelForm):
    profilepic = forms.ImageField(required=False)
    description = forms.CharField(widget=forms.Textarea, required=False, max_length=100)
    likes = forms.CharField(widget=forms.Textarea, required=False, max_length=50)
    dislikes = forms.CharField(widget=forms.Textarea, required=False, max_length=50)

    class Meta:
        model = UserProfile
        fields = ('description', 'likes', 'dislikes', 'profilepic')


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        widgets = {'private_profile': forms.CheckboxInput(attrs={'id': 'i_private_profile'})}
        fields = ['private_profile', 'private_preferences', 'explicit_music']


class ExtendedUserChangeForm(UserChangeForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    password = None

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)

class PlaylistForm(forms.ModelForm):
    name = forms.CharField(max_length=30)
    image = forms.ImageField(required=False)
    description = forms.CharField(widget=forms.Textarea, required=True, max_length=299)
    date_created = datetime.datetime.now()
    is_private = forms.BooleanField(required=False)
    is_shareable = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Playlist
        fields = ('name', 'image', 'is_private', 'is_shareable')

