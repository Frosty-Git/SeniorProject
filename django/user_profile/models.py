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

