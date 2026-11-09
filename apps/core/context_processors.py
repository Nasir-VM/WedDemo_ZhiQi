from __future__ import annotations

from typing import Any

from django.core.cache import cache
from django.http import HttpRequest

from apps.core.models import SystemSetting


def app_context(request: HttpRequest) -> dict[str, Any]:
    context: dict[str, Any] = {
        "company": SystemSetting.load(),
        "currency": "TWD",
        "app_version": "1.0.0",
    }
    if request.user.is_authenticated:
        from apps.expenses.services import pending_review_count
        from apps.notifications.services import unread_count

        context["unread_notifications"] = unread_count(request.user)
        context["pending_review_count"] = pending_review_count(request.user)
        context["nav_cache_buster"] = cache.get(f"navbust:{request.user.pk}", 0)
    return context
