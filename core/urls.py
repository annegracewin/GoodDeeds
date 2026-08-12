# core/urls.py

from django.urls import include, path
from . import views

urlpatterns = [
    # Feed & Users
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('users/', views.UserListView.as_view(), name='users'),
    
    # Posts
    path('create/', views.create_post, name='create-post'),
    path('<uuid:post_id>/like/', views.like_post, name='like-post'),
    path('<uuid:post_id>/verify/', views.verify_post, name='verify-post'),
    path('posts/<uuid:post_id>/', views.post_detail, name='post-detail'),   # ← ADD THIS
    
    # Challenges – keep only one definition
    path('challenges/', views.ChallengeListView.as_view(), name='challenge-list'),
    path('challenges/create/', views.create_challenge, name='create-challenge'),
    path('challenges/<int:challenge_id>/join/', views.join_challenge, name='join-challenge'),
    path('challenges/my/', views.my_challenges, name='my-challenges'),
    
    # Rewards
    path('rewards/', views.RewardListView.as_view(), name='reward-list'),
    path('rewards/<int:reward_id>/redeem/', views.redeem_reward, name='redeem-reward'),
    path('auth/user/', views.current_user, name='current-user'),

    path('<uuid:post_id>/delete/', views.delete_post, name='delete-post'),
   
    
]