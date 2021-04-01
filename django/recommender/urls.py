from django.urls import path
from . import views

app_name = 'recommender'

urlpatterns = [
    path('', views.home, name='home'),
    path('best/', views.searchform_get, name='best'),
    path('bestp/', views.searchform_post, name='bestp'),
    path('results/', views.results, name='results'),
    path('about/', views.about, name='about'),
    path('survey/', views.survey, name='survey'),
    path('top-tracks/', views.top_tracks, name='top-tracks'),
    path('artist/', views.searchArtist_get, name='artist'),
    path('artistp/', views.searchArtist_post, name='artistp'),
    path('song/', views.searchSong_get, name='song'),
    path('songp/', views.searchSong_post, name='songp'),
    path('get_artist/' , views.get_artist_from_passed_value, name ='get_artist'),
    path('song_upvote/', views.song_upvote, name='song_upvote'),
    path('song_downvote/', views.song_downvote, name='song_downvote'),
    path('upr/', views.user_preference_recommender, name='user_preference_recommender')
]