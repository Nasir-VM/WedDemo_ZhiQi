from __future__ import annotations

from django.http import HttpRequest, HttpResponse

from .context import clear_current_request, set_current_request


class AuditContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        set_current_request(request)
        try:
            return self.get_response(request)
        finally:
            clear_current_request()
