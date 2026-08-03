from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'nature_points', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('GoodDeeds Profile', {'fields': ('bio', 'profile_pic', 'location', 'nature_points', 'total_posts')}),
    )