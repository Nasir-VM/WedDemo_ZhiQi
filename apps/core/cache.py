from __future__ import annotations

from django.core.cache import cache

DASHBOARD_VERSION_KEY = "dashboard_version"


def bump_dashboard_version() -> None:

    try:
        cache.incr(DASHBOARD_VERSION_KEY)
    except ValueError:
        cache.set(DASHBOARD_VERSION_KEY, 1, None)


def dashboard_version() -> int:
    return int(cache.get(DASHBOARD_VERSION_KEY, 0) or 0)
