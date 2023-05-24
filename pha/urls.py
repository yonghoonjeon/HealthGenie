from django.urls import path
from .views import register_view, login_view, index, project_list, ProjectCreateView, project_detail, analyze
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', register_view, name='register'),
    path('signin/', login_view, name='login'),
    path('index/', index, name='main'),
    path('projects/', project_list, name='project_list'),
    path('projects/create/', ProjectCreateView.as_view(), name='create_project'),
    path('projects/<int:project_id>/', project_detail, name='project_detail'),
    path('analyze/', analyze, name='analyze'),
]


