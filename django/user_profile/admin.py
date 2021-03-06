from django.contrib import admin
from .models import UserProfile
from .models import Settings
from .models import Preferences
from .models import Playlist

admin.site.register(UserProfile)
admin.site.register(Settings)
admin.site.register(Preferences)
admin.site.register(Playlist)