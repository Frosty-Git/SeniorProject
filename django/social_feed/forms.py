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
    text = forms.CharField(widget=forms.Textarea())
    date_created = datetime.datetime.now()
    
    class Meta:
        model = Post
        fields = ('text',)
    

class CommentForm(forms.ModelForm):
    """
    Form to make a comment on an a Post.
    Last updated: 3/17/21 by Katie Lee, Jacelynn Duranceau, Marc Colin, Joe Frost 
    """
    text = forms.CharField(widget=forms.Textarea(), max_length=200)
    date_created = datetime.datetime.now()

    class Meta:
        model = Comment
        fields = ('text',)