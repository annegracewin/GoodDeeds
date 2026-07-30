from django.urls import path
from . import views

urlpatterns = [
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('users/', views.UserListView.as_view(), name='users'),   # ← NEW
    path('create/', views.create_post, name='create-post'),
    path('<uuid:post_id>/like/', views.like_post, name='like-post'),
    path('<uuid:post_id>/verify/', views.verify_post, name='verify-post'),
]