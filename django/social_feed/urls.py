from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    path('', views.display_posts, name='feed'),
    path('create_post/', views.create_post, name='create_post'),
    # path('createcomment_post/<int:post_id>', views.createcomment_post, name='createcomment_post'),
    # path('<int:post_id>/', views.detail, name='detail'),
]