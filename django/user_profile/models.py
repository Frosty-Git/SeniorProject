from django.db import models

# UserProfile


# Settings
class Settings(models.Model):
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


# Playlist
    user_profile_fk = models.ForeignKey(UserProfile) # Who created the playlist
    music_data_fk = models.ForeignKey(MusicData, null=True) # Songs in the playlist
    name = models.CharField(max_length=30)
    image = models.ImageField(null=True) # Pillow, add upload_to attribute
    upvotes = models.IntegerField(default=0) 
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField(auto_now_add=True)
    theme = models.TextField()  # Genres
    # this_weeks_upvotes = models.IntegerField()
    # length = # Derived
    # num_songs = # Derived
    # num_followers = # Derived
    objects = models.Manager()
