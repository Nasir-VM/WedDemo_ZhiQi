from __future__ import annotations

import hashlib
from dataclasses import dataclass

from django.conf import settings
from django.core.exceptions import ValidationError

ALLOWED_SIGNATURES: tuple[tuple[bytes, str, str], ...] = (
    (b"\xff\xd8\xff", "image/jpeg", "jpg"),
    (b"\x89PNG\r\n\x1a\n", "image/png", "png"),
    (b"%PDF-", "application/pdf", "pdf"),
)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}


@dataclass(frozen=True)
class UploadInfo:
    content_type: str
    extension: str
    size: int
    sha256: str


def inspect_upload(uploaded_file) -> UploadInfo:

    size = getattr(uploaded_file, "size", 0) or 0
    if size <= 0:
        raise ValidationError("檔案為空。")
    if size > settings.MAX_ATTACHMENT_SIZE:
        limit_mb = settings.MAX_ATTACHMENT_SIZE / (1024 * 1024)
        raise ValidationError(f"檔案不可超過 {limit_mb:.0f}MB。")
    name = (getattr(uploaded_file, "name", "") or "").lower()
    extension = "." + name.rsplit(".", 1)[-1] if "." in name else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError("僅允許 JPG、PNG 或 PDF 檔案。")
    uploaded_file.seek(0)
    head = uploaded_file.read(16)
    uploaded_file.seek(0)
    detected = None
    for signature, content_type, ext in ALLOWED_SIGNATURES:
        if head.startswith(signature):
            detected = (content_type, ext)
            break
    if detected is None:
        raise ValidationError("檔案內容不是有效的 JPG、PNG 或 PDF。")
    content_type, ext = detected
    if extension == ".jpeg" and ext == "jpg":
        extension = ".jpg"
    if extension.lstrip(".") != ext:
        raise ValidationError("副檔名與檔案實際內容不符。")
    digest = hashlib.sha256()
    uploaded_file.seek(0)
    for chunk in uploaded_file.chunks():
        digest.update(chunk)
    uploaded_file.seek(0)
    return UploadInfo(
        content_type=content_type, extension=ext, size=size, sha256=digest.hexdigest()
    )
