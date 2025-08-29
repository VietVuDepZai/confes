from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')  # các field cơ bản

class LoginForm(forms.Form):
    user_or_email = forms.CharField(label="Username hoặc Email", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
