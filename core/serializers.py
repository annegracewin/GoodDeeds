from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post

# Get the active User model (custom or default)
User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for Post objects.
    Includes user details and computed fields.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.CharField(source='user.id', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'user_id',
            'username',
            'image_url',
            'caption',
            'hashtags',
            'location',
            'is_verified',
            'verification_score',
            'likes',
            'comments_count',
            'shares',
            'points',
            'created_at',
        ]
        read_only_fields = ['user_id', 'username', 'is_verified', 'verification_score', 'points']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User objects.
    Provides a profile_pic URL (either from model or generated).
    """
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_pic']

    def get_profile_pic(self, obj):
        """
        Returns the user's profile picture URL.
        If the user model has a `profile_pic` field and it's not empty, use it.
        Otherwise, generate a placeholder avatar using UI Avatars API.
        """
        # Check if the user instance has a 'profile_pic' attribute and it's not empty
        if hasattr(obj, 'profile_pic') and obj.profile_pic:
            return obj.profile_pic
        # Fallback: generate a nice avatar from the username
        return f'https://ui-avatars.com/api/?name={obj.username}&background=2e7d32&color=fff&size=62'