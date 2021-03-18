from django import forms
from django.forms.widgets import DateTimeInput
from social_feed.models import *
import datetime


class PostForm(forms.ModelForm):
    """
    Form to submit a text post to the social feed of our website.
    Last updated: 3/17/21 by Katie Lee, Jacelynn Duranceau, Marc Colin, Joe
    Frost
    """
    text = forms.Textarea()
    date_created = datetime.datetime.now()
    
    class Meta:
        model = Post
        fields = ('text',)

# class SongPostForm(PostForm):
#     """
        # Form to share a song post to the social feed. Note this will be shared
        # by way of a button next to songs from search results, playlists, etc.
        # on the site. You will not explicitly click a button to make a song post
        # and select a song to share.
        # Last updated: 3/17/21 by Katie Lee, Jacelynn Duranceau, Marc Colin, Joe
        # Frost
        # """ 
    

class CommentForm(forms.ModelForm):
    """
    Form to make a comment on an a Post.
    Last updated: 3/17/21 by Katie Lee, Jacelynn Duranceau, Marc Colin, Joe Frost 
    """
    text = forms.Textarea()
    date_created = datetime.datetime.now()
    
    class Meta:
        model = Comment
        fields = ('text',)