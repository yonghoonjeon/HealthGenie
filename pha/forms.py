from django import forms
from django.forms.widgets import NumberInput
from .models import User, Project, HealthInfo, Tracking


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


ALLERGY_CHOICES = [
    ('None', 'None'),
    ('gluten', 'Gluten'),
    ('soybeans', 'Soybeans'),
    ('eggs', 'Eggs'),
    ('dairy', 'Diary'),
    ('tree nuts', 'Tree Nuts'),
    ('peanuts', 'Peanuts'),
    ('fish', 'Fish'),
    ('shellfish', 'Shellfish')
]

ACTIVITY_CHOICES = [
    ('sedentary', 'Sedentary'),
    ('moderate', 'Moderate'),
    ('active', 'Active')
]

DIETARY_CHOICES = [
    ('None', 'None'),
    ('vegeterian', 'Vegeterian'),
    ('vegan', 'Vegan'),
    ('halal', 'Halal'),
    ('kosher', 'Kosher'),
    ('gluten_intolerance', 'Gluten Intolerance'),
    ('lactose_intolerance', 'Lactose Intolerance')
]


class HealthInfoForm(forms.ModelForm):
    class Meta:
        model = HealthInfo
        fields = ['allergy_name', 'activity_level', 'dietary_restriction']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['allergy_name'] = forms.ChoiceField(label='Allergy', choices=ALLERGY_CHOICES)
        self.fields['activity_level'] = forms.ChoiceField(label='Activity Level', choices=ACTIVITY_CHOICES)
        self.fields['dietary_restriction'] = forms.ChoiceField(label='Dietary Restriction', choices=DIETARY_CHOICES)


class TrackingForm(forms.ModelForm):
    class Meta:
        model = Tracking
        fields = ['cur_weight']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cur_weight'] = forms.CharField(label='Current Weight (kg)')

