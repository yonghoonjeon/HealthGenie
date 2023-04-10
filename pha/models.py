from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('Email을 입력해주세요.')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        # extra_fields.setdefault('sex', None)
        # extra_fields.setdefault('age', None)
        # extra_fields.setdefault('height', None)
        # extra_fields.setdefault('weight', None)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
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
        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_("username"), max_length=50, blank=True)
    email = models.EmailField(_("email_address"), unique=True)
    is_staff = models.BooleanField(_("staff status"), default=False)
    is_active = models.BooleanField(_("active"), default=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    sex = models.CharField(max_length=6)
    age = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    weight = models.PositiveIntegerField()

    objects = UserManager()
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    email = models.ForeignKey(User, on_delete=models.CASCADE)
    is_achieved = models.BooleanField()
    p_name = models.CharField(max_length=100)
    goal_weight = models.PositiveIntegerField()
    goal_bmi = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class Food(models.Model):
    food_id = models.AutoField(primary_key=True)
    f_name = models.CharField(max_length=100)
    calories = models.PositiveIntegerField()
    protein = models.PositiveIntegerField()
    fat = models.PositiveIntegerField()
    carbs = models.PositiveIntegerField()


class Meal(models.Model):
    meals_id = models.AutoField(primary_key=True)
    food_id = models.ForeignKey(Food, on_delete=models.CASCADE)
    email = models.ForeignKey(User, on_delete=models.CASCADE)
    meal_time = models.DateTimeField()

