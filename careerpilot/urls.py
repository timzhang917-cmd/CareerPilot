"""
URL configuration for careerpilot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include

from analyses import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls")), # 包含accounts应用的url
    path("jobs/", include("jobs.urls")),
    path('',views.home,name='home'),
    # 最新一次分析结果
    path("analysis/", views.analysis_result, name="analysis_result"),

    # 当前用户的历史分析列表
    path(
        "analysis/history/",
        views.analysis_history,
        name="analysis_history",
    ),

    # 查看当前用户指定的一次历史分析结果
    path(
        "analysis/<int:analysis_id>/",
        views.analysis_result,
        name="analysis_detail",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )   # 仅用于本地开发
