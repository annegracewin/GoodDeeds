import uuid
from django.db import models
from django.conf import settings

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    
    image_url = models.URLField(max_length=500, default='https://picsum.photos/800/600')
    caption = models.TextField(max_length=500, blank=True)
    hashtags = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    
    is_verified = models.BooleanField(default=False)
    verification_score = models.FloatField(default=0.0)
    
    likes = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    
    points = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_verified', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.caption[:30]}"