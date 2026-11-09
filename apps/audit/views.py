from __future__ import annotations

import contextlib
import json
from datetime import date

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.audit.models import AuditLog


def _guard(request: HttpRequest) -> None:
    if not request.user.is_authenticated:
        raise PermissionDenied
    if not (request.user.is_admin_role or request.user.role == "auditor"):
        raise PermissionDenied("僅管理員與稽核角色可檢視稽核日誌。")


def audit_list(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    _guard(request)
    queryset = AuditLog.objects.select_related("user").all()
    action = request.GET.get("action", "").strip()
    model_label = request.GET.get("model", "").strip()
    q = request.GET.get("q", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    if action:
        queryset = queryset.filter(action=action)
    if model_label:
        queryset = queryset.filter(model_label=model_label)
    if q:
        queryset = queryset.filter(
            Q(username__icontains=q)
            | Q(object_repr__icontains=q)
            | Q(object_id__icontains=q)
            | Q(ip__icontains=q)
        )
    for raw, lookup in ((date_from, "created_at__date__gte"), (date_to, "created_at__date__lte")):
        if raw:
            with contextlib.suppress(ValueError):
                queryset = queryset.filter(**{lookup: date.fromisoformat(raw)})
    paginator = Paginator(queryset, 50)
    page = paginator.get_page(request.GET.get("page"))
    for log in page:
        log.pretty_changes = json.dumps(log.changes, ensure_ascii=False, indent=2)
    return render(
        request,
        "audit/list.html",
        {
            "page": page,
            "actions": AuditLog.Action.choices,
            "models": (
                AuditLog.objects.exclude(model_label="")
                .values_list("model_label", flat=True)
                .distinct()
                .order_by("model_label")
            ),
            "filters": {
                "action": action,
                "model": model_label,
                "q": q,
                "date_from": date_from,
                "date_to": date_to,
            },
        },
    )
