from django.urls import path
from . import views

app_name = "main"
urlpatterns = [
    path('', views.home, name="home"),
    path('api/signup/', views.singup, name='signup'),
    path('api/login/', views.login, name='signin'),
    path('api/user-info/', views.user_info, name='user_info'),
    path('api/user-mood/', views.user_mood, name='user_mood'),
    path('api/user-data/', views.user_data, name='user_data'),
]