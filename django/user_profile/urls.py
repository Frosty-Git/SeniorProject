from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('signup/', views.sign_up, name='signup'),
    path('logout/', views.logout_request, name='logout'),
    path('login/', views.login_request, name='login'),
    path('profile/<user_id>', views.profile, name='profile'),
    path('settings/<user_id>', views.display_settings, name='settings'),
    path('settings_save/<user_id>', views.settings_save, name='settings_save'),
    path('following/<user_id>', views.display_following, name='following'),
    path('unfollow/<user_id>/<who>', views.unfollow, name='unfollow'),
    # path('userprofile/<user_id>', views.other_profile, name='other_profile'),
    # path('num_followers/<user_id>', views.num_followers, name='num_followers')
]