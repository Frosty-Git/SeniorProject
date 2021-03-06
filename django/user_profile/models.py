from django.db import models
from django.contrib.auth.models import User

# UserProfile
class UserProfile(models.Model):
    user = models.OneToOneField(User, 
                                on_delete=models.CASCADE,
                                primary_key=True,
                                related_name='profile')
    birthdate = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True, max_length=100)
    likes = models.TextField(blank=True, null=True, max_length=50)
    dislikes = models.TextField(blank=True, null=True, max_length=50)
    profilepic = models.ImageField(upload_to='images/', null=True, verbose_name="")
    date_last_update = models.DateTimeField(auto_now_add=True)
    date_created = models.DateTimeField(auto_now_add=True)
    following = models.ManyToManyField(UserProfile)
    playlists_followed = models.ManyToManyField(Playlist)
    preferences = models.OneToOneField(Preferences, on_delete=models.CASCADE)
    settings = models.OneToOneField(Settings, on_delete=models.CASCADE)

    #spotify_id
    #linked_to_spotify = models.BooleanField() maybe not needed

    def __str__(self):
        return self.user.username

# Settings


# Preferences


# Playlist

