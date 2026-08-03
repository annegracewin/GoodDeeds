from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'caption', 'is_verified', 'points', 'likes', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['caption', 'user__username']
    readonly_fields = ['id', 'created_at']