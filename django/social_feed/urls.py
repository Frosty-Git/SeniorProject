from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    path('', views.display_posts, name='feed'),
    path('create_post/', views.create_post, name='create_post'),
    path('create_post_profile/', views.create_post_profile, name='create_post_profile'),
    path('delete_post/<post_id>/<location>', views.delete_post, name='delete_post'),
    path('update_post/', views.update_post, name='update_post'),
    path('popup_post/<post_id>', views.popup_post, name='popup_post'),
    path('share_songpost/', views.popup_songpost, name='songpost'),
    path('share_playlistpost/', views.popup_playlistpost, name='playlistpost'),
    path('upvote/', views.upvote, name='upvote'),
    path('downvote/', views.downvote, name='downvote'),
    path('pop_update_post/<post_id>', views.pop_update_post, name='pop_update_post'),
]