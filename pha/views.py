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
from django.conf import settings
from datetime import datetime
import os
from django.db import connection
import requests
import shutil
import cv2
import numpy as np
import webcolors
import json
from .models import Food, Meal

STANDARD_COLORS = [
    'DarkGrey', 'LawnGreen', 'Crimson', 'LightBlue' , 'Gold', 'BlanchedAlmond', 'Bisque',
    'Aquamarine', 'BlueViolet', 'BurlyWood', 'CadetBlue', 'AntiqueWhite','Azure',
    'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan',
    'DarkCyan', 'DarkGoldenRod',  'DarkKhaki', 'DarkOrange',
    'DarkOrchid', 'DarkSalmon', 'DarkSeaGreen', 'DarkTurquoise', 'DarkViolet',
    'DeepPink', 'DeepSkyBlue', 'DodgerBlue', 'FireBrick', 'FloralWhite',
    'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 'GoldenRod',
    'Salmon', 'Tan', 'HoneyDew', 'HotPink', 'IndianRed', 'Ivory', 'Khaki',
    'Lavender', 'LavenderBlush', 'AliceBlue', 'LemonChiffon', 'LightBlue',
    'LightCoral', 'LightCyan', 'LightGoldenRodYellow', 'LightGray', 'LightGrey',
    'LightGreen', 'LightPink', 'LightSalmon', 'LightSeaGreen', 'LightSkyBlue',
    'LightSlateGray', 'LightSlateGrey', 'LightSteelBlue', 'LightYellow', 'Lime',
    'LimeGreen', 'Linen', 'Magenta', 'MediumAquaMarine', 'MediumOrchid',
    'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen',
    'MediumTurquoise', 'MediumVioletRed', 'MintCream', 'MistyRose', 'Moccasin',
    'NavajoWhite', 'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed',
    'Orchid', 'PaleGoldenRod', 'PaleGreen', 'PaleTurquoise', 'PaleVioletRed',
    'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 'Purple',
    'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Green', 'SandyBrown',
    'SeaGreen', 'SeaShell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue',
    'SlateGray', 'SlateGrey', 'Snow', 'SpringGreen', 'SteelBlue', 'GreenYellow',
    'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'Wheat', 'White',
    'WhiteSmoke', 'Yellow', 'YellowGreen'
]

def from_colorname_to_bgr(color):
    rgb_color = webcolors.name_to_rgb(color)
    result = (rgb_color.blue/255.0, rgb_color.green/255.0, rgb_color.red/255.0)
    return result

def standard_to_bgr(list_color_name):
    standard = []
    for i in range(len(list_color_name)):  # -36 used to match the len(obj_list)
        standard.append(from_colorname_to_bgr(list_color_name[i]))
    return standard

color_list = standard_to_bgr(STANDARD_COLORS)

# Create your views here.
def draw_bboxes_v2(savepath, img, boxes, label_ids, scores, label_names=None, obj_list=None):
    """
    Visualize an image with its bouding boxes
    rgb image + xywh box
    """

    def plot_one_box(img, box, key=None, value=None, color=None, line_thickness=None):
        tl = line_thickness or int(
            round(0.001 * max(img.shape[0:2])))  # line thickness

        coord = [box[0], box[1], box[0] + box[2], box[1] + box[3]]
        c1, c2 = (int(coord[0]), int(coord[1])
                  ), (int(coord[2]), int(coord[3]))
        cv2.rectangle(img, c1, c2, color, thickness=tl + 1)

        if key is not None and value is not None:
            header = f'{key}: {value}'
            tf = max(tl - 2, 2)  # font thickness
            s_size = cv2.getTextSize(
                f' {value}', 0, fontScale=float(tl) / 3, thickness=tf)[0]
            t_size = cv2.getTextSize(
                f'{key}:', 0, fontScale=float(tl) / 3, thickness=tf)[0]
            c2 = c1[0] + t_size[0] + s_size[0] + 15, c1[1] - t_size[1] - 3
            cv2.rectangle(img, c1, c2, color, -1)  # filled
            cv2.putText(img, header, (c1[0], c1[1] - 2), 0, float(tl) / 3, [0, 0, 0],
                        thickness=tf, lineType=cv2.FONT_HERSHEY_SIMPLEX)

    # boxes input is xywh
    boxes = np.array(boxes, np.uint16)
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    for idx, (box, label_id, score) in enumerate(zip(boxes, label_ids, scores)):
        if label_names is not None:
            label = label_names[idx]
        if obj_list is not None:
            label = obj_list[label_id]

        new_color = tuple(i * 255.0 for i in color_list[int(label_id)])

        plot_one_box(
            img_bgr,
            box,
            key=label,
            value='{:.0%}'.format(float(score)),
            color=new_color,
            line_thickness=2)

    cv2.imwrite(savepath, img_bgr)

def index(request):
    return redirect('project_list')


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

    return render(request, 'pha/project_list.html')

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
        email = request.POST.get('email')
        if user:
            login(request, user)
            #store user information in session variables 
            # session = SessionStore(request.session.session_key)
            # session['email'] = user.get_username()
            request.session['email'] = email
            # session.save() 
            return redirect(reverse("main"))
        messages.error(request, "등록되지 않은 사용자입니다.\n정보를 다시 확인해주세요")
        return HttpResponse("오류")

    return render(request, 'pha/login.html')

@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user)
    if request.method == 'POST':
        current_datetime = timezone.now()
        datetime_object = datetime.strptime(current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f"), "%Y-%m-%d %H:%M:%S.%f")
        datetime_object = datetime_object.replace(hour=0, minute=0, second=0, microsecond=0)
        try:
            instance = Tracking.objects.get(user=request.user, update_time__gt=datetime_object)
            form = TrackingForm(request.POST, instance=instance)
        except Tracking.DoesNotExist:
            form = TrackingForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            form.save()
            messages.success(request, "Update successfully!")

        if 'f_name[]' in request.POST:
            food_names = request.POST.getlist('f_name[]')
            meal_types = request.POST.getlist('meal_type[]')
            serving_sizes = request.POST.getlist('serving_size[]')
            ratings = request.POST.getlist('rating[]')

            for i in range(len(food_names)):
                # Get the food name, meal type, serving size, and rating for this meal
                food_name = food_names[i]
                meal_type = meal_types[i]
                serving_size = serving_sizes[i]
                rating = ratings[i]
                if serving_size == '' or meal_type == '' or rating == '':
                    continue

                # Find the corresponding Food object
                try:
                    food = Food.objects.get(f_name=food_name)
                except Food.DoesNotExist:
                    return JsonResponse({'error': 'Food not found.'}, status=404)

                meal = Meal.objects.create(
                    user=request.user,
                    food_id=food,
                    meal_type=meal_type,
                    serving_size=serving_size,
                    rating=rating
                )
                meal.save()

        if 'f_name' in request.POST:
            food_name = request.POST['f_name']
            meal_type = request.POST['meal_type']
            serving_size = request.POST['serving_size']
            rating = request.POST['rating']

            # Find the corresponding Food object
            try:
                food = Food.objects.get(f_name=food_name)
            except Food.DoesNotExist:
                return JsonResponse({'error': 'Food not found.'}, status=404)

            meal = Meal.objects.create(
                user=request.user,
                food_id=food,
                meal_type=meal_type,
                serving_size=serving_size,
                rating=rating
            )
            meal.save()
    else:
        form = TrackingForm()

    if request.method == 'POST' and 'file' in request.FILES:
        try:
            image = request.FILES['file']
        except:
            return JsonResponse({'error': 'Please select an image file.'})

        path = default_storage.save('tmp/' + image.name, ContentFile(image.read()))

        image_path = default_storage.path(path)
        media_path = os.path.join(settings.MEDIA_ROOT, 'uploads', image.name)
        shutil.copyfile(image_path, media_path)

        flask_url = 'http://37ce-34-170-252-194.ngrok-free.app/analyze'

        with open(image_path, 'rb') as img:
            response = requests.post(flask_url, files={'file': img})

        if response.status_code == 200:
            orig_image = cv2.imread(media_path)
            orig_image = np.array(orig_image, dtype=np.uint16)
            orig_image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB)

            response_data = response.json()

            boxes = []
            label_ids = []
            scores = []
            label_names = []
            json_string = response_data["csv_name1"]
            data = json.loads(json_string)
            for item in data:
                boxes.append([item['x'], item['y'], item['w'], item['h']])
                label_ids.append(item['labels'])
                scores.append(item['scores'])
                label_names.append(item['names'])

            draw_bboxes_v2(media_path, orig_image, boxes, label_ids, scores, label_names=label_names)

            image_url = settings.MEDIA_URL + 'uploads/' + image.name

            return render(request, 'pha/project_list.html',
                          {'projects': projects, 'form': form, 'image_url': image_url, 'result': response.json()})
        else:
            return JsonResponse({'error': 'An error occurred while processing the image.'})

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
    streamlit_app_dir = 'C:/Users/hwang/HealthGenie/pha/final_streamlit'
    #subprocess.Popen(['streamlit', 'run', './final_streamlit.py', '--', '--user_id', '4', '--project_id', '12', '--server.headless', 'true'], cwd=streamlit_app_dir)
    #user_id = request.user

    user_email = request.session.get('email')

    with connection.cursor() as cursor:

        user_query = """
                    select user_id 
                    from pha_user
                    where email = %s;
                    """
        cursor.execute(user_query, [user_email])
        user_data = cursor.fetchone()
    user_id = user_data[0]
    subprocess.Popen(['streamlit', 'run', './final_streamlit.py', '--server.headless', 'true', '--', '--user_id', str(user_id), '--project_id', str(project_id)], cwd=streamlit_app_dir)

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