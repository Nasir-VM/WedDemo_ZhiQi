from __future__ import annotations

import logging
from typing import Any

from django.apps import apps
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.audit.models import AuditLog
from apps.audit.services import log_action
from apps.core.utils import jsonable

logger = logging.getLogger("zhiqi.audit")

TRACKED_MODELS = (
    "accounts.User",
    "accounts.Department",
    "accounts.CostCenter",
    "projects.Project",
    "projects.ProjectType",
    "expenses.Expense",
    "expenses.Invoice",
    "expenses.LineItem",
    "expenses.InvoiceAttachment",
    "expenses.Vendor",
    "expenses.ExpenseCategory",
    "core.SystemSetting",
)

EXCLUDED_FIELDS = {"password", "totp_secret", "last_login"}
MAX_VALUE_LENGTH = 500


def _snapshot(instance: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for field in instance._meta.concrete_fields:
        if field.name in EXCLUDED_FIELDS:
            continue
        value = jsonable(getattr(instance, field.attname, None))
        if isinstance(value, str) and len(value) > MAX_VALUE_LENGTH:
            value = value[:MAX_VALUE_LENGTH] + "…"
        data[field.name] = value
    return data


def _diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    changes = {}
    for key in sorted(set(before) | set(after)):
        if before.get(key) != after.get(key):
            changes[key] = {"before": before.get(key), "after": after.get(key)}
    return changes


def _connect() -> None:
    for label in TRACKED_MODELS:
        try:
            model = apps.get_model(label)
        except LookupError:
            continue
        pre_save.connect(
            _pre_save, sender=model, weak=False, dispatch_uid=f"audit.pre_save.{label}"
        )
        post_save.connect(
            _post_save, sender=model, weak=False, dispatch_uid=f"audit.post_save.{label}"
        )
        post_delete.connect(
            _post_delete, sender=model, weak=False, dispatch_uid=f"audit.post_delete.{label}"
        )


def _pre_save(sender, instance, **kwargs) -> None:
    if not instance.pk:
        instance._audit_before = None
        return
    try:
        old = sender._default_manager.get(pk=instance.pk)
    except sender.DoesNotExist:
        instance._audit_before = None
        return
    instance._audit_before = _snapshot(old)


def _post_save(sender, instance, created, **kwargs) -> None:
    if getattr(instance, "_skip_audit", False):
        return
    after = _snapshot(instance)
    if created:
        changes = {"after": after}
        action = AuditLog.Action.CREATE
    else:
        before = getattr(instance, "_audit_before", None)
        if before is None:
            return
        changes = _diff(before, after)
        if not changes:
            return
        action = AuditLog.Action.UPDATE
    log_action(
        action=action,
        model_label=f"{sender._meta.app_label}.{sender._meta.object_name}",
        object_id=instance.pk,
        object_repr=str(instance),
        changes=changes,
    )


def _post_delete(sender, instance, **kwargs) -> None:
    if getattr(instance, "_skip_audit", False):
        return
    log_action(
        action=AuditLog.Action.DELETE,
        model_label=f"{sender._meta.app_label}.{sender._meta.object_name}",
        object_id=instance.pk,
        object_repr=str(instance),
        changes={"before": _snapshot(instance)},
    )


@receiver(user_logged_in, dispatch_uid="audit.user_logged_in")
def on_user_logged_in(sender, request, user, **kwargs) -> None:
    log_action(
        action=AuditLog.Action.LOGIN,
        user=user,
        model_label="accounts.User",
        object_id=user.pk,
        object_repr=str(user),
        request=request,
    )


@receiver(user_logged_out, dispatch_uid="audit.user_logged_out")
def on_user_logged_out(sender, request, user, **kwargs) -> None:
    if user is not None:
        log_action(
            action=AuditLog.Action.LOGOUT,
            user=user,
            model_label="accounts.User",
            object_id=user.pk,
            object_repr=str(user),
            request=request,
        )


@receiver(user_login_failed, dispatch_uid="audit.user_login_failed")
def on_user_login_failed(sender, credentials, request=None, **kwargs) -> None:
    username = str(credentials.get("username", ""))[:150]
    log_action(
        action=AuditLog.Action.LOGIN_FAILED,
        model_label="accounts.User",
        object_repr=username,
        changes={"username": username},
        request=request,
    )


_connect()
