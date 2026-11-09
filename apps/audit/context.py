from __future__ import annotations

import threading

from django.http import HttpRequest

_state = threading.local()


def set_current_request(request: HttpRequest) -> None:
    _state.request = request


def get_current_request() -> HttpRequest | None:
    return getattr(_state, "request", None)


def clear_current_request() -> None:
    _state.request = None
