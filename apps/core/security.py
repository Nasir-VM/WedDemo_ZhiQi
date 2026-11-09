from __future__ import annotations

import ipaddress

from django.conf import settings
from django.http import HttpRequest


def _is_trusted_proxy(remote_addr: str) -> bool:

    if not remote_addr:
        return False
    if remote_addr in settings.TRUSTED_PROXY_IPS:
        return True
    try:
        address = ipaddress.ip_address(remote_addr)
    except ValueError:
        return False
    return address.is_private or address.is_loopback


def get_client_ip(request: HttpRequest) -> str:

    remote = request.META.get("REMOTE_ADDR", "") or ""
    if settings.TRUST_CF_CONNECTING_IP and _is_trusted_proxy(remote):
        candidate = request.META.get("HTTP_CF_CONNECTING_IP", "").strip()
        if candidate:
            try:
                ipaddress.ip_address(candidate)
                return candidate
            except ValueError:
                pass
    return remote


def get_client_ip_from_request(request: HttpRequest | None = None) -> str:

    if request is None:
        return ""
    return get_client_ip(request)


def ratelimit_ip(group: str, request: HttpRequest) -> str:

    return get_client_ip(request)
