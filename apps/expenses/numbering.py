from __future__ import annotations

from datetime import date

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.core.db import retry_on_locked
from apps.expenses.models import DocumentSequence


@retry_on_locked
@transaction.atomic
def next_expense_number(prefix: str = "志", at: date | None = None) -> str:

    target_date = at or timezone.localdate()
    period = target_date.strftime("%Y%m")
    sequence, _ = DocumentSequence.objects.get_or_create(
        scope="expense", period=period, defaults={"last_value": 0}
    )
    DocumentSequence.objects.filter(pk=sequence.pk).update(last_value=F("last_value") + 1)
    sequence.refresh_from_db(fields=["last_value"])
    return f"{prefix}-{period}-{sequence.last_value:04d}"
