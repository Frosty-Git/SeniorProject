from django.db import models
from django.contrib.auth.models import User

from django.core.validators import MinValueValidator, MaxValueValidator

# UserProfile
class UserProfile(models.Model):
    """
    UserProfile
    creates a user profile, extends existing Django User
    last updated: 3/10/2021 by Katie Lee and Marc Colin and Jacelynn Duranceau
    """
    user = models.OneToOneField(User, 
                                on_delete=models.CASCADE,
                                primary_key=True,
                                related_name='profile')
    birthdate = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True, max_length=100)
    likes = models.TextField(blank=True, null=True, max_length=50)
    dislikes = models.TextField(blank=True, null=True, max_length=50)
    profilepic = models.ImageField(upload_to='images/', null=True, verbose_name="", blank=True)
    date_last_update = models.DateTimeField(auto_now_add=True)
    date_created = models.DateTimeField(auto_now_add=True)
    linked_to_spotify = models.BooleanField(default=False)
    users_followed = models.ManyToManyField('self', 
                                        through="FollowedUser",
                                        related_name='followers',
                                        symmetrical=False)
    playlists_followed = models.ManyToManyField('Playlist',
                                        through="FollowedPlaylist",
                                        related_name='playlists_followed',
                                        symmetrical=False)
    num_followers = models.PositiveIntegerField(default=0)
    num_following = models.PositiveIntegerField(default=0)
    access_token = models.CharField(default='No Value', max_length=255)
    refresh_token = models.CharField(default='No Value', max_length=255)
    expires_at = models.CharField(default='No Value', max_length=50)
    scope = models.TextField(default='No Value')
    songs_liked = models.ManyToManyField('SongId', 
                                        through="SongToUser",
                                        related_name='songs_liked',
                                        symmetrical=False)
    liked_songs_playlist_fk = models.ForeignKey('Playlist', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username

# Settings
class Settings(models.Model):
    """
    Model for Settings. Each user can turn his or her settings on or off, which
    will affect the functionality of the website.
    Last updated: 3/6/21 by Jacelynn Duranceau
    """
    user_profile_fk = models.ForeignKey(UserProfile, on_delete=models.CASCADE, default=None)
    private_profile = models.BooleanField(default=False)
    private_playlists = models.BooleanField(default=False)  # will be removes
    private_preferences = models.BooleanField(default=False)
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
    Kevin Magill 03/29/2021 
    creates model for the database
    relationship is defined in UserProfile
    Last updated: 3/30/21 by Marc Colin, Jacelynn Duranceau, Katie Lee
    """
    user_profile_fk = models.ForeignKey(UserProfile, on_delete=models.CASCADE, default=None)
    # 0 to 1
    acousticness = models.FloatField(blank=True, default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    # 0 to 1
    danceability = models.FloatField(blank=True, default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    # 0 to 1
    energy = models.FloatField(blank=True, default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    # 0 to 1
    instrumentalness = models.FloatField(blank=True, default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    # 0 to 1
    speechiness = models.FloatField(blank=True, default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    # -60 to 0
    loudness = models.FloatField(blank=True, default=-30, validators=[MinValueValidator(-60.0), MaxValueValidator(0.0)])
    # 50 to 150
    tempo = models.FloatField(blank=True, default=100, validators=[MinValueValidator(50.0), MaxValueValidator(150.0)])
    # 0 to 1
    valence = models.FloatField(blank=True, default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    def __str__(self):
        return "Preferences"

# Playlist
class Playlist(models.Model):
    """
    Model for playlists created by users on the site. Songs can be added or
    deleted to the playlists, and playlists can be liked or disliked by other
    users.
    Last updated: 3/27/21 by Jacelynn Duranceau
    """
    user_profile_fk = models.ForeignKey(UserProfile, on_delete=models.CASCADE, default=None) # Who created the playlist
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='images/', null=True, verbose_name="", blank=True) # Pillow
    upvotes = models.IntegerField(default=0) 
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)
    is_shareable = models.BooleanField(default=True)
    #theme = models.TextField(null=True, blank=True)  # Genres
    # this_weeks_upvotes = models.IntegerField()
    # length = # Derived
    # num_songs = # Derived
    # num_followers = # Derived
    objects = models.Manager()
    class Meta:
        ordering = ('-date_last_updated',)

    def __str__(self):
        return self.name


# Followed User
class FollowedUser(models.Model):
    """
    Model representing a bridging table that contains foreign keys for a 
    who a user follows.
    Last updated: 3/10/21 by Katie Lee, Jacelynn Duranceau, Marc Colin, Kevin Magill
    """
    user_from = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_from_u')
    user_to = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_to')
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)
    
    def __str__(self):
        return "Followed User"
    


# Followed Playlist
class FollowedPlaylist(models.Model):
    """
    Model representing a bridging table that contains playlists followed by
    a user.
    Last updated: 3/10/21 by Marc Colin, Katie Lee, Kevin Magill, Jacelynn Duranceau
    """
    user_from = models.ForeignKey(UserProfile, related_name='user_from_p', on_delete=models.CASCADE)
    playlist_to = models.ForeignKey(Playlist, related_name='playlist_to', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-date_created',)
    
    def __str__(self):
        return "Followed Playlist"

class SongId(models.Model):
    """
    Model based on Spotify IDs and gets the attributes for the track.
    Last updated: 3/31/21 by Katie Lee, Jacelynn Duranceau, Marc Colin
    """
    spotify_id = models.CharField(max_length=30, default='', primary_key=True)
    artists = models.TextField()
    name = models.TextField()
    explicit = models.BooleanField()
    acousticness = models.FloatField()
    danceability = models.FloatField()
    energy = models.FloatField()
    instrumentalness = models.FloatField()
    speechiness = models.FloatField()
    loudness = models.FloatField()
    tempo = models.FloatField()
    valence = models.FloatField()

    def __str__(self):
        return self.name

class SongOnPlaylist(models.Model):
    """
    Model representing a table between a song and a playlist.
    Last updated: 3/23/21 by Joe Frost, Marc Colin, Katie Lee, Jacelynn Duranceau, 
    Kevin Magill
    """
    playlist_from = models.ForeignKey(Playlist, related_name='playlist_from', on_delete=models.CASCADE)
    spotify_id = models.ForeignKey(SongId, related_name='song_to', on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "Song"

class SongToUser(models.Model):
    """
    Model representing if a user has liked a song from the search.
    Last updated: 3/31/21 by  Marc Colin, Katie Lee, Jacelynn Duranceau,
    """
    user_from = models.ForeignKey(UserProfile, related_name='song_user_from', on_delete=models.CASCADE)
    songid_to = models.ForeignKey(SongId, related_name='user_song_to', on_delete=models.CASCADE)
    vote = models.TextField()   # Either Like or Dislike
    date_created = models.DateTimeField(auto_now_add=True)