from __future__ import annotations

from django.urls import path

from apps.core import master_views

app_name = "master"

urlpatterns = [
    path("", master_views.master_index, name="index"),
    path("<slug:kind>/", master_views.master_list, name="list"),
    path("<slug:kind>/new/", master_views.master_create, name="create"),
    path("<slug:kind>/<int:pk>/edit/", master_views.master_update, name="update"),
    path("<slug:kind>/<int:pk>/delete/", master_views.master_delete, name="delete"),
]
