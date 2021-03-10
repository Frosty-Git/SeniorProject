from django.contrib import admin
from .models import *

admin.site.register(UserProfile)
admin.site.register(Settings)
admin.site.register(Preferences)
admin.site.register(Playlist)
admin.site.register(FollowedUser)
admin.site.register(FollowedPlaylist)
admin.site.register(Song_On_Playlist)