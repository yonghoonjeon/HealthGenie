from django.http import JsonResponse, HttpResponse
from .forms import UserRegisterForm
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, authenticate, logout


# Create your views here.
def index(request):
    return HttpResponse("안녕하세요 PHA에 오신것을 환영합니다.")


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