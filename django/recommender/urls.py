from django.urls import path
from . import views

app_name = 'recommender'

urlpatterns = [
    path('', views.home, name='home'),
    path('best/', views.searchform_get, name='best'),
    path('bestp/', views.searchform_post, name='bestp'),
]
 