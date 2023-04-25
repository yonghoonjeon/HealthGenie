from django.http import JsonResponse, HttpResponse
from .forms import UserRegisterForm,ProjectForm
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Project
import streamlit as st
import subprocess
import os

# Create your views here.
def index(request):
    return redirect('project_list')

def streamlit(request):
    # os.chdir('/Users/hwang/Desktop/HealthGenie/HealthGenie/pha')
    # os.system("streamlit run streamlit_app.py")
    streamlit_app_dir = '/Users/hwang/Desktop/HealthGenie/HealthGenie/pha'
    subprocess.Popen(['streamlit', 'run', 'streamlit_app.py', '--server.headless', 'true'], cwd=streamlit_app_dir)
    return render(request, 'pha/home.html')

def register_view(request):
    """
    사용자 등록 템플릿 view
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "가입이 정상적으로 완료되었습니다 \n ")
            return render(request, 'pha/login.html')
        else:
            messages.error(request, "가입이 정상적으로 진행되지 않았습니다\n계속해서 문제가 발생하면 관리자에게 문의해주세요")
            return render(request, 'pha/register.html', {'form': form})
    else:
        form = UserRegisterForm
    return render(request, 'pha/register.html', {'form': form})


def login_view(request):
    """
    사용자 로그인 템플릿 view
    """
    if request.method == 'POST':
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect(reverse("main"))
        messages.error(request, "등록되지 않은 사용자입니다.\n정보를 다시 확인해주세요")
        return HttpResponse("오류")

    return render(request, 'pha/login.html')

@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user)
    context = {'projects': projects}
    return render(request, 'pha/project_list.html', context)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'pha/create_project.html'
    success_url = reverse_lazy('project_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

def project_detail(request, project_id):
    project = Project.objects.get(pk=project_id)
    context = {'project': project}
    return render(request, 'pha/project_detail.html', context)

def streamlit_view(request):
    # Streamlit 코드 작성
    st.title("Hello, Streamlit!")
    st.write("This is a Streamlit app embedded in a Django app.")