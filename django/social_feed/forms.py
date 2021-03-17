from django import forms
from django.forms.widgets import DateTimeInput
from social_feed.models import *
import datetime


class PostForm(forms.ModelForm):
    """
    """
    text = forms.Textarea()
    date_created = datetime.datetime.now()
    
    class Meta:
        model = Post
        fields = ('text',)

# class SongPostForm(PostForm):
#     """
#     """
    

# class CommentForm(forms.ModelForm):
#     """
#     """
#     class Meta:
#         model = Comment
#         fields = ('comment_text',)