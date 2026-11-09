from __future__ import annotations

from django.contrib import admin

from apps.core.models import SystemSetting


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ("company_name", "approval_threshold", "default_tax_rate", "updated_at")
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request) -> bool:
        return not SystemSetting.objects.exists()

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
