from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('process-command/', views.process_voice_command, name='process_command'),
    path('history/', views.command_history, name='command_history'),
] 