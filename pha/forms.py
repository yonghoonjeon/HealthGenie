from django import forms
from .models import User,Project


class UserRegisterForm(forms.ModelForm):
    # password = forms.CharField()
    # widgets = {'password': forms.PasswordInput}
    class Meta:
        model = User
        fields = ['user_name', 'email', 'password', 'sex', 'age', 'height', 'weight']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput()

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['p_name', 'is_achieved', 'goal_weight', 'goal_bmi', 'goal_type', 'start_time', 'end_time']