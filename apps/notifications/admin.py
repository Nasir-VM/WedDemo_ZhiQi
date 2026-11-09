from __future__ import annotations

from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "level", "is_read", "created_at")
    list_filter = ("level", "is_read", "created_at")
    search_fields = ("user__username", "title", "message")
    date_hierarchy = "created_at"
    raw_id_fields = ("user",)
