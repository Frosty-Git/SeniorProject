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
    path('unfollow/<user_id>/<who>', views.unfollow, name='unfollow'),
    path('update_profile/', views.update_profile, name='update_profile'),

    # Password related URLs
    path('account_setting/', auth_views.PasswordChangeView.as_view(
            template_name='settings/account_setting.html',
            success_url='/user/password_change_done/'), name='account_setting'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(
            template_name='settings/password_change_done.html',), name='password_change_done'),
    
    # path('userprofile/<user_id>', views.other_profile, name='other_profile'),
    # path('num_followers/<user_id>', views.num_followers, name='num_followers')
]