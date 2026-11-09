from __future__ import annotations

from django.urls import path

from apps.expenses import views

app_name = "reports"

urlpatterns = [
    path("", views.report_view, name="index"),
]
