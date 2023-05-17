from django import forms
from django.forms.widgets import NumberInput
from .models import User, Project, Tracking


class UserRegisterForm(forms.ModelForm):
    # password = forms.CharField()
    # widgets = {'password': forms.PasswordInput}
    class Meta:
        model = User
        fields = ['user_name', 'email', 'password', 'sex', 'age', 'height', 'weight']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget = forms.EmailInput()
        self.fields['password'].widget = forms.PasswordInput()

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


GOAL_CHOICES = [
    ('diet', 'Diet'),
    ('putting on weight', 'Putting on weight'),
]


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['p_name', 'cur_weight', 'goal_weight', 'goal_bmi', 'goal_type', 'start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['p_name'] = forms.CharField(label='Project name')
        self.fields['cur_weight'] = forms.CharField(label='Current weight (kg)')
        self.fields['goal_weight'] = forms.CharField(label='Goal weight (kg)')
        self.fields['goal_bmi'] = forms.CharField(label='Goal bmi')
        self.fields['start_time'] = forms.DateField(label='Start date', widget=NumberInput(attrs={'type': 'date'}))
        self.fields['end_time'] = forms.DateField(label='End date', widget=NumberInput(attrs={'type': 'date'}))
        self.fields['goal_type'] = forms.ChoiceField(label='Select your goal type', choices=GOAL_CHOICES)


class TrackingForm(forms.ModelForm):
    class Meta:
        model = Tracking
        fields = ['cur_weight']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cur_weight'] = forms.CharField(label='Current Weight (kg)')

