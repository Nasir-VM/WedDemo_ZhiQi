from __future__ import annotations

from django.core.exceptions import ValidationError

WEIGHTS = (1, 2, 1, 2, 1, 2, 4, 1)


def is_valid_tax_id(value: str) -> bool:

    if not value or len(value) != 8 or not value.isdigit():
        return False
    total = 0
    for digit, weight in zip(value, WEIGHTS, strict=True):
        product = int(digit) * weight
        total += product // 10 + product % 10
    if total % 10 == 0:
        return True
    return value[6] == "7" and (total + 1) % 10 == 0


def validate_tax_id(value: str) -> None:
    if value and not is_valid_tax_id(value):
        raise ValidationError("統一編號檢查碼不正確，請確認 8 位數字。")
