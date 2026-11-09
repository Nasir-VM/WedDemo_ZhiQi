from __future__ import annotations

from django.contrib import admin

from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "username", "action", "model_label", "object_repr", "ip")
    list_filter = ("action", "model_label", "created_at")
    search_fields = ("username", "object_repr", "object_id", "ip")
    readonly_fields = (
        "user",
        "username",
        "action",
        "model_label",
        "object_id",
        "object_repr",
        "changes",
        "ip",
        "user_agent",
        "created_at",
    )
    date_hierarchy = "created_at"

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
