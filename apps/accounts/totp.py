from __future__ import annotations

import base64
import hashlib
import hmac
import os
import struct
import time
from urllib.parse import quote, urlencode


def generate_secret(byte_length: int = 20) -> str:
    return base64.b32encode(os.urandom(byte_length)).decode("ascii").rstrip("=")


def _decode_secret(secret: str) -> bytes:
    padded = secret + "=" * ((8 - len(secret) % 8) % 8)
    return base64.b32decode(padded, casefold=True)


def hotp(secret: str, counter: int, digits: int = 6) -> str:
    digest = hmac.new(_decode_secret(secret), struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{value % (10**digits):0{digits}d}"


def totp(secret: str, at: float | None = None, step: int = 30, digits: int = 6) -> str:
    timestamp = time.time() if at is None else at
    return hotp(secret, int(timestamp // step), digits=digits)


def verify_totp(secret: str, code: str, at: float | None = None, window: int = 1) -> bool:
    if not secret or not code or not code.isdigit():
        return False
    timestamp = time.time() if at is None else at
    current = int(timestamp // 30)
    normalized = code.strip()
    return any(
        hmac.compare_digest(hotp(secret, current + offset), normalized)
        for offset in range(-window, window + 1)
    )


def provisioning_uri(secret: str, account: str, issuer: str = "志氣核銷") -> str:
    label = quote(f"{issuer}:{account}")
    params = urlencode(
        {
            "secret": secret,
            "issuer": issuer,
            "algorithm": "SHA1",
            "digits": 6,
            "period": 30,
        }
    )
    return f"otpauth://totp/{label}?{params}"
