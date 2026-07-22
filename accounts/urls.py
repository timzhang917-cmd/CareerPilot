from django.urls import path

from . import views


urlpatterns = [
    path("register/", views.register, name="register"), 
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
] # 注册页面的url，还要让项目总路由识别到它