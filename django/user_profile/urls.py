from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('signup/', views.sign_up, name='signup'),
    path('logout/', views.logout_request, name='logout'),
    path('login/', views.login_request, name='login'),
]