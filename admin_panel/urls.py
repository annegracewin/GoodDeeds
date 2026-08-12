from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('challenges/', views.challenge_list, name='challenges'),
    path('challenges/<int:pk>/approve/', views.approve_challenge, name='approve_challenge'),
    path('challenges/<int:pk>/reject/', views.reject_challenge, name='reject_challenge'),
    path('challenges/create/', views.create_challenge, name='create_challenge'),
    path('challenges/<int:pk>/edit/', views.edit_challenge, name='edit_challenge'),
    path('challenges/<int:pk>/delete/', views.delete_challenge, name='delete_challenge'),
    path('rewards/', views.reward_list, name='rewards'),
    path('rewards/create/', views.create_reward, name='create_reward'),
    path('rewards/<int:pk>/edit/', views.edit_reward, name='edit_reward'),
    path('rewards/<int:pk>/delete/', views.delete_reward, name='delete_reward'),
    path('users/', views.user_list, name='users'),
    path('users/<int:pk>/toggle/', views.toggle_user_active, name='toggle_user'),
    path('sponsors/', views.sponsor_list, name='sponsors'),
    path('sponsors/create/', views.create_sponsor, name='create_sponsor'),
    path('sponsors/<int:pk>/edit/', views.edit_sponsor, name='edit_sponsor'),
    path('sponsors/<int:pk>/delete/', views.delete_sponsor, name='delete_sponsor'),
]