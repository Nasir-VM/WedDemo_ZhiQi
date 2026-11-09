from __future__ import annotations

import re

from django.core.exceptions import ValidationError


class ComplexityValidator:

    def validate(self, password: str, user=None) -> None:
        checks = [
            (re.search(r"[A-Z]", password), "大寫英文字母"),
            (re.search(r"[a-z]", password), "小寫英文字母"),
            (re.search(r"\d", password), "數字"),
            (re.search(r"[^A-Za-z0-9]", password), "符號"),
        ]
        missing = [label for matched, label in checks if not matched]
        if missing:
            raise ValidationError(
                "密碼必須包含" + "、".join(missing) + "。",
                code="password_too_simple",
            )

    def get_help_text(self) -> str:
        return "密碼至少 10 碼，且需包含大寫、小寫、數字與符號。"
