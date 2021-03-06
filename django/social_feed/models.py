from typing import Text
from django.db import models

# Post
class Post(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    date_last_updated = models.DateTimeField(auto_now_add=True)

# SongPost
class SongPost(Post):
    song = models.ForeignKey(Musicdata)
    def __str__(self):
        return self.song

# PlaylistPost
class PlaylistPost(Post):
    playlist = models.ForeignKey(Playlist)

    def __str__(self):
        return self.playlist
# Comment

