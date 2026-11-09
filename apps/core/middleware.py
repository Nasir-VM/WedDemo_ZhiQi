from __future__ import annotations

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden

from .security import get_client_ip


class SecurityHeadersMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(self), microphone=(), geolocation=(), payment=(), usb=()",
        )
        response.headers.setdefault("X-Permitted-Cross-Domain-Policies", "none")
        return response


class AdminIPAllowlistMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        prefix = f"/{settings.ADMIN_URL_PATH}/"
        allowed = settings.ADMIN_ALLOWED_IPS
        if allowed and request.path.startswith(prefix) and get_client_ip(request) not in allowed:
            return HttpResponseForbidden("管理後台僅限允許的來源 IP。")
        return self.get_response(request)


class NoCacheHTMLMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if content_type.startswith("text/html") and request.user.is_authenticated:
            response["Cache-Control"] = "private, no-store, max-age=0"
            response["X-No-Cache"] = "1"
        return response


class DashboardVersionCacheMixin:

    @staticmethod
    def bump_version() -> None:
        try:
            cache.incr("dashboard_version")
        except ValueError:
            cache.set("dashboard_version", 1, None)
