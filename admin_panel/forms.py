from django import forms
from core.models import Challenge, Reward, Sponsor

class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['title', 'description', 'category', 'points_reward', 'start_date', 'end_date', 'image', 'is_featured']

class RewardForm(forms.ModelForm):
    class Meta:
        model = Reward
        fields = ['name', 'description', 'category', 'points_cost', 'image', 'stock_quantity', 'is_active']

class SponsorForm(forms.ModelForm):
    class Meta:
        model = Sponsor
        fields = ['name', 'email', 'website', 'logo', 'contact_person', 'is_active']