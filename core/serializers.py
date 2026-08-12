from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Challenge, ChallengeParticipant, Reward, RewardRedemption,Like

User = get_user_model()


# Ensure PostSerializer includes the 'image' field
class PostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.CharField(source='user.id', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'user_id', 'username', 'image', 'image_url', 'caption',
            'hashtags', 'location', 'is_verified', 'verification_score', 
            'verification_status', 'likes', 'comments_count', 'shares', 
            'points', 'created_at', 'is_liked'
        ]
        read_only_fields = ['is_verified', 'verification_score', 'verification_status', 'points']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False
class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_pic']

    def get_profile_pic(self, obj):
        if hasattr(obj, 'profile_pic') and obj.profile_pic:
            return obj.profile_pic
        return f'https://ui-avatars.com/api/?name={obj.username}&background=2e7d32&color=fff&size=62'


class ChallengeSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'category',
            'created_by', 'created_by_username',
            'start_date', 'end_date', 'points_reward',
            'participants_count', 'is_active', 'is_featured',
            'image', 'created_at', 'updated_at'
        ]


class ChallengeParticipantSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    challenge_title = serializers.CharField(source='challenge.title', read_only=True)

    class Meta:
        model = ChallengeParticipant
        fields = [
            'id', 'challenge', 'user', 'user_username', 'challenge_title',
            'status', 'posts_count', 'points_earned', 'completed_at',
            'created_at', 'updated_at'
        ]


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = '__all__'


class RewardRedemptionSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    reward_name = serializers.CharField(source='reward.name', read_only=True)

    class Meta:
        model = RewardRedemption
        fields = [
            'id', 'user', 'user_username', 'reward', 'reward_name',
            'status', 'points_spent', 'redemption_code',
            'approved_at', 'fulfilled_at', 'created_at'
        ]