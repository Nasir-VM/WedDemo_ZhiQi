from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django_ratelimit.decorators import ratelimit as _ratelimit


def rate_limit(
    *,
    key: str | Callable[..., str] = "ip",
    rate: str,
    method: str | None = "POST",
) -> Callable[[Callable[..., HttpResponse]], Callable[..., HttpResponse]]:

    def decorator(view: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
        @functools.wraps(view)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            guarded = _ratelimit(key=key, rate=rate, method=method, block=False)(view)
            response = guarded(request, *args, **kwargs)
            if getattr(request, "limited", False):
                return render(request, "core/429.html", status=429)
            return response

        return wrapper

    return decorator
