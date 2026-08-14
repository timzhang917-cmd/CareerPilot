from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import RegisterForm

def get_user_home_route(user):
     # 根据用户身份返回登录后的目标路由名称

    is_hr = user.groups.filter(
        name="HR",
    ).exists()

    if is_hr:
        return "hr_dashboard"

    return "home"


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = form.save()

                # HR 身份使用 Django Group 保存，
                # 不需要修改 Django 默认 User 模型。
                if form.cleaned_data["account_type"] == "hr":
                    hr_group, _ = Group.objects.get_or_create(
                        name="HR",
                    )
                    user.groups.add(hr_group)

            login(request, user)

            # 根据刚刚保存的账户身份决定注册后的页面。
            return redirect(
                get_user_home_route(user)
            )
    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
        },
    )


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(
            request,
            data=request.POST,
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # HR 登录后进入 Dashboard，
            # 普通用户继续进入网站首页。
            return redirect(
                get_user_home_route(user)
            )
    else:
        form = AuthenticationForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
        },
    )


def logout_view(request):
    if request.method == "POST":
        logout(request)

    return redirect("home")