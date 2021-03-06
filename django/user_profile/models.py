from django.db import models
from django.contrib.auth.models import User

# UserProfile
class UserProfile(models.Model):
    """
    UserProfile
    Katie Lee and Marc Colin 03/06/2021 12:00PM
    creates a user profile,
    extends existing Django User
    """
    user = models.OneToOneField(User, 
                                on_delete=models.CASCADE,
                                primary_key=True,
                                related_name='profile')
    birthdate = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True, max_length=100)
    likes = models.TextField(blank=True, null=True, max_length=50)
    dislikes = models.TextField(blank=True, null=True, max_length=50)
    profilepic = models.ImageField(upload_to='images/', null=True)
    date_last_update = models.DateTimeField(auto_now_add=True)
    date_created = models.DateTimeField(auto_now_add=True)
    following_fk = models.ManyToManyField("UserProfile")
    playlists_followed_fk = models.ManyToManyField(Playlist)
    preferences_fk = models.OneToOneField(Preferences, on_delete=models.CASCADE)
    settings_fk = models.OneToOneField(Settings, on_delete=models.CASCADE)

    #spotify_id
    #linked_to_spotify = models.BooleanField() maybe not needed

    def __str__(self):
        return self.user.username

# Settings
class Settings(models.Model):
    """
    Model for Settings. Each user can turn his or her settings on or off, which
    will affect the functionality of the website.
    Last updated: 3/6/21 by Jacelynn Duranceau
    """
    user_id = models.ForeignKey(UserProfile)
    private_profile = models.BooleanField(default=False)
    private_playlists = models.BooleanField(default=False)
    light_mode = models.BooleanField(default=False)
    explicit_music = models.BooleanField(default=False)
    live_music = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return "Setting"

# Preferences
class Preferences(models.Model):
    """
    Preferences
    Kevin Magill 03/06/2020 12:00 P.M.
    creates model for the database
    relationship is defined in UserProfile
    """
    accousticness = models.TextField(blank = True, null = True)
    danceability = models.TextField(blank = True, null = True)
    energy = models.TextField(blank = True, null = True)
    instrumentalness = models.TextField(blank = True, null = True)
    speechiness = models.TextField(blank = True, null = True)
    loudness = models.TextField(blank = True, null = True)
    tempo = models.TextField(blank = True, null = True)
    valence = models.TextField(blank = True, null = True)

    def __str__(self):
        return "Preferences"

# Playlist
class Playlist(models.Model):
    """
    Model for playlists created by users on the site. Songs can be added or
    deleted to the playlists, and playlists can be liked or disliked by other
    users.
    Last updated: 3/6/21 by Jacelynn Duranceau
    """
    user_profile_fk = models.ForeignKey(UserProfile) # Who created the playlist
    music_data_fk = models.ManyToManyField(MusicData, null=True, on_delete=models.CASCADE) # Songs in the playlist
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='images/', null=True) # Pillow
    upvotes = models.IntegerField(default=0) 
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField(auto_now_add=True)
    theme = models.TextField()  # Genres
    # this_weeks_upvotes = models.IntegerField()
    # length = # Derived
    # num_songs = # Derived
    # num_followers = # Derived
    objects = models.Manager()
    def __str__(self):
        return self.name
