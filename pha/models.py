from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, user_name, email, password, **extra_fields):
        if not email:
            raise ValueError('Please enter your email address.')
        email = self.normalize_email(email)
        user = self.model(user_name=user_name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, user_name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, user_name, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('sex', 'others')
        extra_fields.setdefault('age', '9999')
        extra_fields.setdefault('height', '9999')
        extra_fields.setdefault('weight', '9999')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('is_staff=True일 필요가 있습니다.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser=True일 필요가 있습니다.')
        return self._create_user(user_name, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    MALE = 'male'
    FEMALE = 'female'

    SEX = (
        (MALE, 'Male'),
        (FEMALE, 'Female')
    )
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(_("staff status"), default=False)
    is_active = models.BooleanField(_("active"), default=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    sex = models.CharField(max_length=6, choices=SEX)
    age = models.PositiveIntegerField()
    height = models.FloatField()
    weight = models.FloatField()

    objects = UserManager()
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ['user_name']

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_achieved = models.BooleanField(default=False)
    p_name = models.CharField(max_length=100)
    cur_weight = models.FloatField()
    goal_weight = models.FloatField()
    goal_bmi = models.PositiveIntegerField()
    goal_type = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class Food(models.Model):
    food_id = models.AutoField(primary_key=True)
    f_name = models.CharField(max_length=100)
    calories = models.FloatField()
    protein = models.FloatField()
    fat = models.FloatField()
    carbs = models.FloatField()
    ref_serving_size = models.FloatField()
    cuisine = models.CharField(max_length=100)
    ingredients = models.CharField(max_length=255)
    allergen = models.CharField(max_length=100)
    dietary_restriction = models.CharField(max_length=100)
    flavor_profile = models.CharField(max_length=100)
    food_category = models.CharField(max_length=100)


class Meal(models.Model):
    meals_id = models.AutoField(primary_key=True)
    food_id = models.ForeignKey(Food, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal_time = models.DateTimeField(auto_now=True)
    meal_type = models.CharField(max_length=100)
    serving_size = models.FloatField()
    rating = models.PositiveIntegerField()


class Tracking(models.Model):
    class Meta:
        unique_together = (('update_time', 'user'),)
    track_id = models.AutoField(primary_key=True)
    update_time = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cur_weight = models.FloatField()


class HealthInfo(models.Model):
    health_info = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    allergy_name = models.CharField(max_length=100)
    activity_level = models.CharField(max_length=100)
    update_time = models.DateTimeField(auto_now=True)
    dietary_restriction = models.CharField(max_length=100)

