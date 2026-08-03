import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    
    image_url = models.URLField(max_length=500, default='https://picsum.photos/800/600')
    caption = models.TextField(max_length=500, blank=True)
    hashtags = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    
    is_verified = models.BooleanField(default=False)
    verification_score = models.FloatField(default=0.0)
    verification_status = models.CharField(max_length=20, default='pending')
    
    likes = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    
    points = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional: link to a challenge
    challenge = models.ForeignKey('Challenge', on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_verified', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.caption[:30]}"


class Challenge(models.Model):
    CATEGORIES = [
        ('environment', 'Environment'),
        ('social', 'Social'),
        ('education', 'Education'),
        ('health', 'Health'),
        ('community', 'Community'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORIES)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_challenges')
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    points_reward = models.IntegerField(default=10)
    participants_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    image = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_progress(self, user):
        return Post.objects.filter(user=user, challenge=self, is_verified=True).count()


class ChallengeParticipant(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('participating', 'Participating'),
        ('completed', 'Completed'),
        ('verified', 'Verified'),
    ]
    
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='challenge_participations')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    posts_count = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['challenge', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"


class Reward(models.Model):
    REWARD_TYPES = [
        ('gift_card', 'Gift Card'),
        ('tangible', 'Tangible Gift'),
        ('voucher', 'Voucher'),
        ('digital', 'Digital Reward'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=REWARD_TYPES)
    points_cost = models.IntegerField()
    image = models.URLField(blank=True, null=True)
    stock_quantity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    provider_details = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.points_cost} pts)"


class RewardRedemption(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='redemptions')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, related_name='redemptions')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    points_spent = models.IntegerField()
    
    redemption_code = models.CharField(max_length=100, blank=True, null=True)
    redemption_details = models.JSONField(default=dict)
    
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_redemptions')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.reward.name}"