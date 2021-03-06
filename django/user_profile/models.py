from django.db import models

# UserProfile


# Settings


# Preferences
# Kevin Magill 03/06/2020 12:00 P.M.
# creates model for the database
# relationship is defined in UserProfile
class Preferences(models.Model):
    accousticness = models.TextField(blank = True, null = True)
    danceability = models.TextField(blank = True, null = True)
    energy = models.TextField(blank = True, null = True)
    instrumentalness = models.TextField(blank = True, null = True)
    speechiness = models.TextField(blank = True, null = True)
    loudness = models.TextField(blank = True, null = True)
    tempo = models.TextField(blank = True, null = True)
    valence = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.accousticness
# Playlist

