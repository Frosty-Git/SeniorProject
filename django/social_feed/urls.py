from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    path('', views.display_posts, name='feed'),
    path('create_post/', views.create_post, name='create_post'),
    path('create_post_profile/', views.create_post_profile, name='create_post_profile'),
    path('delete_post/<post_id>', views.delete_post, name='delete_post'),
    path('<post_id>', views.create_comment, name='comment'),
    path('update_post/', views.update_post, name='update_post'),
    path('popup_post/<post_id>', views.popup_post, name='popup_post'),
    path('share_songpost/', views.popup_songpost, name='songpost'),
    path('upvote/', views.upvote, name='upvote'),
    path('downvote/', views.downvote, name='downvote'),
    path('delete_comment/<comment_id>', views.delete_comment, name='delete_comment'),
    path('update_comment/', views.update_comment, name='update_comment'),
    path('pop_update_post/<post_id>', views.pop_update_post, name='pop_update_post'),
]