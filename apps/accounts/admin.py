from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import CostCenter, Department, User


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "parent", "is_active")
    search_fields = ("code", "name")


@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "department", "is_active")
    list_filter = ("department", "is_active")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "get_full_name", "role", "department", "is_active")
    list_filter = ("role", "department", "is_active", "is_staff")
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "志氣核銷",
            {
                "fields": (
                    "role",
                    "department",
                    "cost_center",
                    "job_title",
                    "employee_no",
                    "phone",
                    "must_change_password",
                    "totp_enabled",
                )
            },
        ),
    )
    readonly_fields = ("last_password_change",)
