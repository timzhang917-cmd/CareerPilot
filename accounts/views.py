"""
AI Usage Declaration:
-This file contains code generated with help of AI tools.
-Tool Used: ChatGPT
-Date Generated: 2026-08
-ChatGPT was used to look up and ensure usage of Django's built-in components,
and the HR role verification logic (line32-43) was used by AI-generated code.

I have reviewed, tested, and understood the AI-generated code.
"""

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import RegisterForm

def decide_where_you_go(user): # jump based on user role

    is_hr = user.groups.filter(
        name="HR",
    ).exists()  # judge if the user is in HR group
    if is_hr:
        return "hr_dashboard"
    return "home" # jump to home page for job seekers

def register(request): # user registration process
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                # HR role is saved in HR Django Group,
                # no need to modify the default User model.
                if form.cleaned_data["account_type"] == "hr":
                    hr_group, _ = Group.objects.get_or_create(
                        name="HR",
                    )
                    user.groups.add(hr_group)

            login(request, user)

            # call decide_where_you_go function.
            return redirect(
                decide_where_you_go(user)
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

def login_view(request):  # user login process
    if request.method == "POST":
        form = AuthenticationForm(
            request,
            data=request.POST,
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # return to the page that required login, only if it is on this site
            next_url = request.GET.get("next", "")
            if url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            # HR enters Dashboard，job seeker enters Home page.
            return redirect(
                decide_where_you_go(user)
            )
    else:
        form = AuthenticationForm()

    return render(
        request,
        "accounts/login.html",
        {"form": form,},
    )


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("home")