from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'user'

urlpatterns = [
    path('signup/', views.sign_up, name='signup'),
    path('logout/', views.logout_request, name='logout'),
    path('login/', views.login_request, name='login'),
    path('profile/<user_id>', views.profile, name='profile'),
    path('settings/<user_id>', views.display_settings, name='settings'),
    path('settings_save/<user_id>', views.settings_save, name='settings_save'),
    path('following/<user_id>', views.display_following, name='following'),
    path('followers/<user_id>', views.display_followers, name='followers'),
    path('unfollow/<user_id>/<who>', views.unfollow, name='unfollow'),
    path('follow/<user_id>/<who>', views.follow, name='follow'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('user_list/', views.user_list, name='user_list'),
    path('userprofile/<user_id>', views.other_profile, name='other_profile'),
    path('playlists/<user_id>', views.get_playlists, name='get_playlists'),
    path('playlist/<playlist_id>', views.get_songs_playlist, name='get_songs_playlist'),
    path('createplaylist/', views.create_playlist_popup, name='create_playlist_popup'),
    path('addsong/<query>', views.add_song_to_playlist, name='add_song_popup'),
    path('editplaylist/', views.edit_playlist_popup, name='edit_playlist_popup'),
    path('deleteplaylist/<playlist_id>', views.delete_playlist, name='delete_playlist'),
    path('deletesong/<playlist_id>/<sop_pk>', views.delete_song, name='delete_song'),
    path('link_spotify/', views.link_spotify, name='link_spotify'),
    path('token/', views.save_token_redirect, name='save_token_redirect'),
    #path('playlist/<playlist_id>', views.create_playlist, name='create_playlist'),
    # path('num_followers/<user_id>', views.num_followers, name='num_followers')
    

    # Password related URLs
    path('account_setting/', auth_views.PasswordChangeView.as_view(
            template_name='settings/account_setting.html',
            success_url='/user/password_change_done/'), name='account_setting'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(
            template_name='settings/password_change_done.html',), name='password_change_done'),
]