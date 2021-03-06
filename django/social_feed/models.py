from django.user_profile.models import UserProfile
from typing import Text
from django.db import models
from user_profile.models import *

# Post
class Post(models.Model):
    """
    Author:  Joseph Frost
    Created: 2021.03.06
    Creates the Post model for the DB.
    """
    date_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    date_last_updated = models.DateTimeField(auto_now_add=True)
    upvotes = models.IntegerField(default=0)
    user_profile_fk = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

# SongPost


# PlaylistPost


# Comment
class Comment(models.Model):
    """
    Author:  Joseph Frost
    Created: 2021.03.06
    Creates the Comment model for the DB.
    """
    date_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    date_last_updated = models.DateTimeField(auto_now_add=True)
    upvotes = models.IntegerField(default=0)
    post_fk = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.text
