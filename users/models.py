from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Override groups and user_permissions to avoid reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='users_user_groups',          # unique name
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='users_user_permissions',     # unique name
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    # Your custom fields
    bio = models.TextField(blank=True, max_length=500)
    profile_pic = models.URLField(blank=True, max_length=500)
    location = models.CharField(blank=True, max_length=255)
    nature_points = models.IntegerField(default=0)
    total_posts = models.IntegerField(default=0)

    def __str__(self):
        return self.username