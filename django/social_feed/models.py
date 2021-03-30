from typing import Text
from django.db import models
from user_profile.models import UserProfile, Playlist

# Post
class Post(models.Model):
    """
    Author: Joseph Frost
    Created: 2020.03.06
    Creates a Post model for the db. The post is a post on the social
    feed created by the user. 
    """
    date_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    date_last_updated = models.DateTimeField(auto_now_add=True)
    upvotes = models.IntegerField(default=0)
    user_profile_fk = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    type_post = models.TextField(default="Post")
    users_voted = models.ManyToManyField(UserProfile, 
                                        through="PostUserVote",
                                        related_name='user_votes',
                                        symmetrical=False)

    def __str__(self):
        return self.text


# SongPost
class SongPost(Post):
    """
    SongPost PlaylistPost
    Tucker Elliott 3/6/2021
    Created models for Posts including a song or a playlist
    SongPost and PlaylistPost models inherit from Post
    """
    song = models.TextField(max_length=30)
    
    def __str__(self):
        return self.song

# PlaylistPost
class PlaylistPost(Post):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)

    def __str__(self):
        return self.playlist

# Comment
class Comment(models.Model):
    """
    Author: Joseph Frost
    Created: 2020.03.06
    Creates a Comment model for the db. The comment is a comment on
    a post on the social feed.
    """
    date_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    date_last_updated = models.DateTimeField(auto_now_add=True)
    upvotes = models.IntegerField(default=0)
    post_fk = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_profile_fk = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class PostUserVote(models.Model):
    """
    Bridging table for Post and User. Keeps track of all votes
    Last updated: 3/30/21 by Marc Colin, Katie Lee
    """
    user_from = models.ForeignKey(UserProfile, related_name='user_from_up', on_delete=models.CASCADE)
    post_to = models.ForeignKey(Post, related_name='post_to_up', on_delete=models.CASCADE)
    vote = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-date_created',)
    
    def __str__(self):
        return "PostUserUpvote"