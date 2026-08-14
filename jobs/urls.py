from django.urls import path

from . import views


urlpatterns = [
    path("", views.job_search, name="job_search"),
    path("applications/", views.my_applications, name="my_applications"),
    path("hr/", views.hr_dashboard, name="hr_dashboard"),
]
