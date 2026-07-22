from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout
from django.shortcuts import redirect, render

from .forms import RegisterForm

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save() # 新用户保存到SQLite数据库
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})

def logout_view(request):
    if request.method == "POST":
        logout(request)

    return redirect("home")
