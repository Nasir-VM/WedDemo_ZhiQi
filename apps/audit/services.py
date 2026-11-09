from __future__ import annotations

from typing import Any

from django.http import HttpRequest

from apps.audit.context import get_current_request
from apps.audit.models import AuditLog
from apps.core.security import get_client_ip
from apps.core.utils import jsonable


def log_action(
    *,
    action: str,
    user: Any = None,
    model_label: str = "",
    object_id: str | int = "",
    object_repr: str = "",
    changes: dict[str, Any] | None = None,
    request: HttpRequest | None = None,
) -> AuditLog | None:
    request = request or get_current_request()
    request_user = getattr(request, "user", None) if request is not None else None
    if user is None and request_user is not None and request_user.is_authenticated:
        user = request_user
    ip = get_client_ip(request) if request is not None else None
    user_agent = ""
    if request is not None:
        user_agent = request.META.get("HTTP_USER_AGENT", "")[:255]
    try:
        return AuditLog.objects.create(
            user=user if getattr(user, "pk", None) else None,
            username=getattr(user, "username", "") or "",
            action=action,
            model_label=model_label[:100],
            object_id=str(object_id)[:64],
            object_repr=object_repr[:255],
            changes=changes or {},
            ip=ip or None,
            user_agent=user_agent,
        )
    except Exception:
        import logging

        logging.getLogger("zhiqi.audit").exception("寫入稽核日誌失敗")
        return None


def log_export(user: Any, *, kind: str, count: int, filters: dict[str, Any]) -> None:
    log_action(
        action=AuditLog.Action.EXPORT,
        user=user,
        model_label="expenses.Expense",
        object_repr=f"{kind} 匯出 {count} 筆",
        changes={
            "format": kind,
            "count": count,
            "filters": {k: jsonable(v) for k, v in filters.items()},
        },
    )
