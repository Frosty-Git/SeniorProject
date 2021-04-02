from django.contrib import admin
from .models import *

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(SongPost)
admin.site.register(PlaylistPost)
admin.site.register(PostUserVote)