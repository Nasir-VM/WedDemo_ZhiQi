from __future__ import annotations

from django.contrib.staticfiles import finders
from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache


def healthz(request: HttpRequest) -> JsonResponse:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "error"}, status=503)
    return JsonResponse({"status": "ok"})


def manifest(request: HttpRequest) -> HttpResponse:
    path = finders.find("manifest.webmanifest")
    if not path:
        return HttpResponse(status=404)
    with open(path, "rb") as handle:
        content = handle.read()
    response = HttpResponse(content, content_type="application/manifest+json")
    response["Cache-Control"] = "public, max-age=3600"
    return response


@never_cache
def service_worker(request: HttpRequest) -> HttpResponse:
    path = finders.find("js/sw.js")
    if not path:
        return HttpResponse(status=404)
    with open(path, "rb") as handle:
        content = handle.read()
    response = HttpResponse(content, content_type="application/javascript")
    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


def offline(request: HttpRequest) -> HttpResponse:
    return render(request, "core/offline.html")


def ratelimited(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    return render(request, "core/429.html", status=429)


def error_400(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    return render(request, "core/400.html", status=400)


def error_403(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    return render(request, "core/403.html", status=403)


def error_404(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    return render(request, "core/404.html", status=404)


def error_500(request: HttpRequest) -> HttpResponse:
    return render(request, "core/500.html", status=500)
