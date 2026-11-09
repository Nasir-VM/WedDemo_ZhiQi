from __future__ import annotations

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.tax import is_valid_tax_id, validate_tax_id
from apps.core.utils import csv_safe, quantize_money, safe_next_url
from apps.expenses.uploads import inspect_upload


def test_tax_id_checksum():
    assert is_valid_tax_id("04595257")
    assert is_valid_tax_id("10458575")
    assert not is_valid_tax_id("12345678")
    assert not is_valid_tax_id("1234")


def test_validate_tax_id_raises():
    with pytest.raises(ValidationError):
        validate_tax_id("12345678")


def test_quantize_money_half_up():
    assert quantize_money(Decimal("1.005")) == Decimal("1.01")
    assert quantize_money("2.344") == Decimal("2.34")


def test_csv_safe_blocks_formula_injection():
    assert csv_safe("=cmd") == "'=cmd"
    assert csv_safe("+1") == "'+1"
    assert csv_safe("-1") == "'-1"
    assert csv_safe("@x") == "'@x"
    assert csv_safe("normal") == "normal"


def test_safe_next_url_rejects_external(rf):
    request = rf.get("/")
    request.META["HTTP_HOST"] = "testserver"
    assert safe_next_url(request, "https://evil.example/") == "/"
    assert safe_next_url(request, "/expenses/") == "/expenses/"


def test_inspect_upload_accepts_png():
    upload = SimpleUploadedFile(
        "receipt.png", b"\x89PNG\r\n\x1a\n" + b"0" * 32, content_type="image/png"
    )
    info = inspect_upload(upload)
    assert info.content_type == "image/png"
    assert info.extension == "png"
    assert len(info.sha256) == 64


def test_inspect_upload_rejects_mismatched_extension():
    upload = SimpleUploadedFile(
        "receipt.pdf", b"\x89PNG\r\n\x1a\n" + b"0" * 32, content_type="application/pdf"
    )
    with pytest.raises(ValidationError):
        inspect_upload(upload)


def test_inspect_upload_rejects_fake_content():
    upload = SimpleUploadedFile("receipt.png", b"not-an-image", content_type="image/png")
    with pytest.raises(ValidationError):
        inspect_upload(upload)
