from django import forms
from django.forms.widgets import DateTimeInput
from social_feed.models import *
import datetime


class PostForm(forms.ModelForm):
    """
    """
    text = forms.CharField(widget=forms.Textarea(), max_length=100)
    date_created = datetime.datetime.now()
    
    class Meta:
        model = Post
        fields = ('text',)

# class SongPostForm(PostForm):
#     """
#     """
    

class CommentForm(forms.ModelForm):
    """
    """
    text = forms.CharField(widget=forms.Textarea(), max_length=100)
    date_created = datetime.datetime.now()

    class Meta:
        model = Comment
        fields = ('text',)