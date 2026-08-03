from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """
    A custom form that uses our custom User model.
    """
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


# Optional: custom AuthenticationForm (not strictly required, but good practice)
class CustomAuthenticationForm(AuthenticationForm):
    """
    A custom authentication form that uses our custom User model.
    """
    class Meta:
        model = User
        fields = ('username', 'password')