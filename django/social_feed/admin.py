from django.contrib import admin
from .models import Post
from .models import Comment
from .models import SongPost
from .models import PlaylistPost

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(SongPost)
admin.site.register(PlaylistPost)