from django.urls import path
from . import views

urlpatterns = [
    # Feed & Users
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('users/', views.UserListView.as_view(), name='users'),
    
    # Posts
    path('create/', views.create_post, name='create-post'),
    path('<uuid:post_id>/like/', views.like_post, name='like-post'),
    path('<uuid:post_id>/verify/', views.verify_post, name='verify-post'),
    
    # Challenges
    path('challenges/', views.ChallengeListView.as_view(), name='challenges'),
    path('challenges/create/', views.create_challenge, name='create-challenge'),
    path('challenges/<int:challenge_id>/join/', views.join_challenge, name='join-challenge'),
    path('challenges/my/', views.my_challenges, name='my-challenges'),
]