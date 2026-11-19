from django.urls import path

from . import views

urlpatterns = [
    path("chat/", views.chat, name="assistant_chat"),
    path("history/<int:analysis_id>/", views.history, name="assistant_history"),
]
