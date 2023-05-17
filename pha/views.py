from django.http import JsonResponse, HttpResponse
from .forms import UserRegisterForm, ProjectForm, TrackingForm
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Project, Tracking
import streamlit as st
import subprocess
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from PIL import Image
from datetime import datetime
import os
import io

# Create your views here.
def index(request):
    return redirect('project_list')

def streamlit(request):
    # os.chdir('/Users/hwang/Desktop/HealthGenie/HealthGenie/pha')
    # os.system("streamlit run streamlit_app.py")
    streamlit_app_dir = '/Users/yjhwang/HealthGenie/pha'
    subprocess.Popen(['streamlit', 'run', 'daye_streamlit_2.py', '--server.headless', 'true'], cwd=streamlit_app_dir)
    return render(request, 'pha/home.html')

import base64
import cv2
import numpy as np
import requests
from PIL import Image
import shutil


from django.views.decorators.csrf import csrf_exempt

import json

# def analyze(request):
#     result = None
#     if request.method == 'POST':
#         if 'image' in request.FILES:
#             image_file = request.FILES['image']
#             # 이미지를 POST 요청으로 보내기 위해 임시 파일로 저장합니다.
#             with open(image_file.name, 'wb') as f:
#                 f.write(image_file.read())
#
#             # API를 호출합니다.
#             api_url = 'http://ce97-34-126-161-185.ngrok-free.app/analyze'
#             file = {'image': open(image_file.name, 'rb')}
#             response = requests.post(api_url, files=file)
#
#             # 결과 JSON을 가져옵니다.
#             result = response.json()
#             return render(request, 'pha/analyze.html', {'result': result})
def analyze(request):
    if request.method == 'POST':
        try:
            image = request.FILES['file']
        except:
            return JsonResponse({'error': 'Please select an image file.'})

        path = default_storage.save('tmp/' + image.name, ContentFile(image.read()))

        # 이미지 파일을 static 파일 디렉토리에 복사
        image_path = default_storage.path(path)
        media_path = os.path.join(settings.MEDIA_ROOT, 'uploads', image.name)
        shutil.copyfile(image_path, media_path)

        # 이 부분에 Flask 애플리케이션의 호스트 및 포트를 입력하세요.
        flask_url = 'http://a209-34-83-252-103.ngrok-free.app/analyze'

        with open(image_path, 'rb') as img:
            response = requests.post(flask_url, files={'file': img})
        os.remove(image_path)  # 임시 파일 삭제

        if response.status_code == 200:
            image_url = settings.MEDIA_URL + 'uploads/' + image.name
            print(image_url)
            return render(request, 'pha/analyze.html', {'image_url': image_url, 'result': response.json()})
        else:
            return JsonResponse({'error': 'An error occurred while processing the image.'})

    return render(request, 'pha/analyze.html')


def classify_image(request):
    if request.method == 'POST':
        # try to get the uploaded file from the request
        try:
            uploaded_file = request.FILES['image']
        except KeyError:
            error_message = "No image file found."
            return render(request, 'pha/classify.html', {'error_message': error_message})

        # Define the API endpoint and parameters
        api_key = "d9b5f98d641f40748fb64aa423495b87"
        input_url = 'https://api.spoonacular.com/food/images/classify'
        params = {'apiKey': api_key}

        # Send a POST request to the API endpoint and store the response
        response = requests.post(input_url, params=params, files={'file': uploaded_file})

        # Check if the request was successful
        if response.status_code == 200:
            # Extract the data from the response
            data = response.json()

            # Get the class of the food item with the highest probability
            food_class = data['category']

            # Get the probability of the predicted class
            probability = data['probability']

        else:
            # If the request was not successful, display an error message
            food_class = None
            probability = None
            error_message = f"Request error: {response.status_code}"
            return render(request, 'pha/classify.html', {'error_message': error_message})

        # Render the HTML template with the classification results
        return render(request, 'pha/classify.html', {'food_class': food_class, 'probability': probability})

    else:
        # Render the HTML template with the image upload form
        return render(request, 'pha/classify.html')

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
    if request.method == 'POST':
        # get current datetime
        current_datetime = timezone.now()
        # Convert the datetime string to a datetime object
        datetime_object = datetime.strptime(current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f"), "%Y-%m-%d %H:%M:%S.%f")
        # modified datetime
        datetime_object = datetime_object.replace(hour=0, minute=0, second=0, microsecond=0)
        # Check if a record with the given datetime exists
        try:
            instance = Tracking.objects.get(user=request.user, update_time__gt=datetime_object)
            form = TrackingForm(request.POST, instance=instance)
        except Tracking.DoesNotExist:
            # Create a new record with the form data
            form = TrackingForm(request.POST)
        if form.is_valid():
            # Save the form with the currently logged-in user
            obj = form.save(commit=False)
            # Assign the currently logged-in user
            obj.user = request.user
            # Redirect or return a response
            form.save()
            messages.success(request, "Update successfully!")
    else:
        form = TrackingForm()
    context = {'projects': projects, 'form': form}
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
    streamlit_app_dir = '/Users/yonghoonjeon/Documents/PycharmProjects/HealthGenie/pha'
    subprocess.Popen(['streamlit', 'run', 'daye_streamlit_3.py', '--server.headless', 'true'], cwd=streamlit_app_dir)

    if request.method == 'POST':
        # try to get the uploaded file from the request
        try:
            uploaded_file = request.FILES['image']
        except KeyError:
            error_message = "No image file found."
            return render(request, 'pha/project_detail.html', {'error_message': error_message, 'project': project})

        # Define the API endpoint and parameters
        api_key = "d9b5f98d641f40748fb64aa423495b87"
        input_url = 'https://api.spoonacular.com/food/images/classify'
        params = {'apiKey': api_key}

        # Send a POST request to the API endpoint and store the response
        response = requests.post(input_url, params=params, files={'file': uploaded_file})

        # Check if the request was successful
        if response.status_code == 200:
            # Extract the data from the response
            data = response.json()

            # Get the class of the food item with the highest probability
            food_class = data['category']

            # Get the probability of the predicted class
            probability = data['probability']

            # Render the HTML template with the classification results
            return render(request, 'pha/project_detail.html', {'food_class': food_class, 'probability': probability, 'project': project})

        else:
            # If the request was not successful, display an error message
            food_class = None
            probability = None
            error_message = f"Request error: {response.status_code}"
            return render(request, 'pha/project_detail.html', {'error_message': error_message, 'project': project})

    else:
        # Render the HTML template with the project details
        context = {'project': project}
        return render(request, 'pha/project_detail.html', context)

def streamlit_view(request):
    # Streamlit 코드 작성
    st.title("Hello, Streamlit!")
    st.write("This is a Streamlit app embedded in a Django app.")