from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    path('', views.display_posts, name='feed'),
    path('create_post/', views.create_post, name='create_post'),
    path('delete_post/<post_id>', views.delete_post, name='delete_post'),
    path('<post_id>', views.create_comment, name='comment'),
    path('update_post/', views.update_post, name='update_post'),
    path('popup_post/<post_id>', views.popup_post, name='popup_post'),
    path('share_songpost/', views.popup_songpost, name='songpost'),
    path('upvote/', views.upvote, name='upvote'),
    path('downvote/', views.downvote, name='downvote'),
]