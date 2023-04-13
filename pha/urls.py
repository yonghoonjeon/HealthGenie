from django.urls import path
from .views import register_view, login_view, index
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup', register_view, name='register'),
    path('signin', login_view, name='login'),
    path('index', index, name='main')
]

