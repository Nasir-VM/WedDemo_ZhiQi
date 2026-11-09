from __future__ import annotations

import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse


def _is_exempt(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


class IdleTimeoutMiddleware:

    EXEMPT = ("/static/", "/healthz", "/manifest.webmanifest", "/sw.js", "/offline/")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and not _is_exempt(request.path, self.EXEMPT):
            now = time.time()
            last = request.session.get("_last_activity")
            if last and now - float(last) > settings.SESSION_IDLE_TIMEOUT:
                logout(request)
                messages.info(request, "因閒置過久，已自動登出。")
                return redirect(f"{reverse('accounts:login')}?next={request.path}")
            request.session["_last_activity"] = now
        return self.get_response(request)


class ForcePasswordChangeMiddleware:

    ALLOWED = (
        "/accounts/password-change/",
        "/accounts/logout/",
        "/accounts/totp/",
        "/static/",
        "/healthz",
        "/manifest.webmanifest",
        "/sw.js",
        "/offline/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, "user", None)
        if (
            user is not None
            and user.is_authenticated
            and user.must_change_password
            and not _is_exempt(request.path, self.ALLOWED)
        ):
            messages.warning(request, "首次登入或密碼已重設，請先變更密碼。")
            return redirect("accounts:password_change")
        return self.get_response(request)


class TwoFactorMiddleware:

    ALLOWED = (
        "/accounts/totp/",
        "/accounts/logout/",
        "/accounts/password-change/",
        "/static/",
        "/healthz",
        "/manifest.webmanifest",
        "/sw.js",
        "/offline/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, "user", None)
        if (
            user is not None
            and user.is_authenticated
            and user.totp_enabled
            and not request.session.get("totp_verified")
            and not _is_exempt(request.path, self.ALLOWED)
        ):
            return redirect("accounts:totp_verify")
        return self.get_response(request)
