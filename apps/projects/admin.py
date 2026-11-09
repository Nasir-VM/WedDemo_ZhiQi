from __future__ import annotations

from django.contrib import admin

from apps.projects.models import Project, ProjectType


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    search_fields = ("code", "name")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "project_type",
        "department",
        "status",
        "budget_total",
        "spent_amount",
    )
    list_filter = ("status", "budget_control", "department", "project_type")
    search_fields = ("code", "name")
    readonly_fields = ("spent_amount", "created_at", "updated_at")
