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
    path("analysis/history/", views.analysis_history, name="analysis_history",),

    # 查看当前用户指定的一次历史分析结果
    path(
        "analysis/<int:analysis_id>/",  # 数字非随机，来自analysis数据库表中的主键id
        views.analysis_result,
        name="analysis_detail",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )   # 仅用于本地开发
