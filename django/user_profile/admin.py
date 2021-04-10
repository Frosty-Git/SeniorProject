from django.contrib import admin
from .models import *
from django.contrib.sessions.models import Session

admin.site.register(UserProfile)
admin.site.register(Settings)
admin.site.register(Preferences)
admin.site.register(Playlist)
admin.site.register(FollowedUser)
admin.site.register(FollowedPlaylist)
admin.site.register(SongOnPlaylist)
admin.site.register(Session)
admin.site.register(SongId)
admin.site.register(SongToUser)
