from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include

from analyses import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls")), 
    path("jobs/", include("jobs.urls")),
    path('',views.home,name='home'),

    path("analysis/", views.analysis_result, name="analysis_result"),


    path("analysis/history/", views.analysis_history, name="analysis_history",),

    path(
        "analysis/<int:analysis_id>/",  # id is not random，from primary key of Analysis model
        views.analysis_result,
        name="analysis_detail",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )   