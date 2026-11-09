from __future__ import annotations

from django.urls import path

from apps.dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="index"),
    path("tv/", views.tv_mode, name="tv"),
    path("tv/data/", views.tv_data, name="tv_data"),
]
