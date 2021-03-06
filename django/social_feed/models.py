from typing import Text
from django.db import models
from user_profile.models import *

# Post
class Post(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    date_last_updated = models.DateTimeField(auto_now_add=True)
    upvotes = models.IntegerField(default=0)
    user_profile_fk = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

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
class Comment(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    date_last_updated = models.DateTimeField(auto_now_add=True)
    upvotes = models.IntegerField(default=0)
    post_fk = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.text
