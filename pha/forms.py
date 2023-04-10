from django import forms
from .models import User


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField()
    widgets = {'password': forms.PasswordInput(),}

    class Meta:
        model = User
        fields = ['user_name', 'email', 'password', 'sex', 'age', 'height', 'weight']

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user