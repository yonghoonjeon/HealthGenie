from django import forms
from .models import User


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField()
    widgets = {'password': forms.PasswordInput(),}

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'sex', 'age', 'height', 'weight']
