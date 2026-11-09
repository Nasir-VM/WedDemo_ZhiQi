from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F, Q, QuerySet, Sum
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.models import AuditLog
from apps.audit.services import log_action
from apps.core.cache import bump_dashboard_version, dashboard_version
from apps.core.db import retry_on_locked
from apps.core.models import SystemSetting
from apps.core.security import get_client_ip
from apps.core.utils import jsonable, quantize_money
from apps.expenses.models import ApprovalLog, Expense, Invoice, InvoiceAttachment
from apps.expenses.permissions import can_act, visible_expenses
from apps.notifications.services import notify, notify_many
from apps.projects.models import Project

logger = logging.getLogger("zhiqi.expenses")

SORT_WHITELIST = {
    "-apply_date",
    "apply_date",
    "-total_amount",
    "total_amount",
    "number",
    "-number",
    "status",
    "-status",
    "-created_at",
}

ACTION_TARGET = {
    "submit": Expense.Status.SUBMITTED,
    "claim": Expense.Status.MANAGER_REVIEW,
    "exec_approve": Expense.Status.FINANCE_REVIEW,
    "finance_approve": Expense.Status.APPROVED,
    "pay": Expense.Status.PAID,
    "return": Expense.Status.RETURNED,
    "reject": Expense.Status.REJECTED,
}


class ConcurrentModification(Exception):
    pass


class BudgetExceeded(Exception):
    pass


def review_statuses_for(user: User) -> list[str]:
    if user.is_admin_role:
        return [Expense.Status.EXEC_REVIEW]
    if user.role == User.Role.FINANCE:
        return [Expense.Status.FINANCE_REVIEW]
    if user.role == User.Role.MANAGER:
        return [Expense.Status.SUBMITTED, Expense.Status.MANAGER_REVIEW]
    return []


def pending_review_count(user: User) -> int:
    statuses = review_statuses_for(user)
    if not statuses:
        return 0
    key = f"pending:{user.pk}:{dashboard_version()}"
    cached = cache.get(key)
    if cached is not None:
        return int(cached)
    queryset = visible_expenses(user).filter(status__in=statuses).exclude(applicant=user)
    count = queryset.count()
    cache.set(key, count, 20)
    return count


def check_project_budget(project: Project | None, amount: Decimal) -> str | None:
    if project is None:
        return None
    projected = project.spent_amount + amount
    if projected <= project.budget_total:
        return None
    message = (
        f"計畫「{project.name}」預算不足：預算 {project.budget_total:,.0f}、"
        f"已核銷 {project.spent_amount:,.0f}、本次 {amount:,.0f}。"
    )
    if project.budget_control == Project.BudgetControl.BLOCK:
        raise BudgetExceeded(message)
    return message


@retry_on_locked
def create_expense(*, applicant: User, data: dict[str, Any]) -> Expense:
    with transaction.atomic():
        expense = Expense(applicant=applicant, **data)
        if not expense.department_id:
            raise ValidationError("申請人尚未設定部門，無法建立核銷單。")
        expense.save()
        ApprovalLog.objects.create(
            expense=expense,
            actor=applicant,
            action=ApprovalLog.Action.CREATE,
            to_status=expense.status,
            comment="建立核銷單",
        )
    transaction.on_commit(bump_dashboard_version)
    return expense


@retry_on_locked
def update_expense(
    *,
    expense: Expense,
    expected_version: int,
    data: dict[str, Any],
    actor: User,
) -> Expense:

    with transaction.atomic():
        if not expense.is_editable:
            raise ValidationError("此核銷單已鎖定，無法修改。")
        updated = Expense.objects.filter(
            pk=expense.pk,
            version=expected_version,
            status__in=[Expense.Status.DRAFT, Expense.Status.RETURNED],
        ).update(**data, version=F("version") + 1, updated_at=timezone.now())
        if not updated:
            raise ConcurrentModification("資料已被其他人更新，請重新載入後再試。")
        expense.refresh_from_db()
        log_action(
            action=AuditLog.Action.UPDATE,
            user=actor,
            model_label="expenses.Expense",
            object_id=expense.pk,
            object_repr=str(expense),
            changes={field: {"after": jsonable(value)} for field, value in data.items()}
            | {"version": {"after": expense.version}},
        )
        ApprovalLog.objects.create(
            expense=expense,
            actor=actor,
            action=ApprovalLog.Action.UPDATE,
            from_status=expense.status,
            to_status=expense.status,
            comment="更新單頭資料",
        )
    transaction.on_commit(bump_dashboard_version)
    return expense


def _notify_after_action(
    expense: Expense, action: str, actor: User, comment: str, target_status: str
) -> None:
    url = reverse("expenses:detail", args=[expense.pk])
    label = expense.number
    if action == "submit":
        managers = list(
            User.objects.filter(
                role=User.Role.MANAGER, department=expense.department, is_active=True
            ).exclude(pk=actor.pk)
        )
        notify_many(
            managers,
            "新的核銷單待審核",
            f"{actor} 送審 {label}，金額 {expense.total_amount:,.0f} 元。",
            url,
            "warning",
        )
    elif action in {"manager_approve", "exec_approve"}:
        if target_status == Expense.Status.EXEC_REVIEW:
            recipients = list(
                User.objects.filter(role=User.Role.ADMIN, is_active=True).exclude(pk=actor.pk)
            )
        else:
            recipients = list(
                User.objects.filter(role=User.Role.FINANCE, is_active=True).exclude(pk=actor.pk)
            )
        notify_many(
            recipients,
            "核銷單待財務／加簽審核",
            f"{label} 已由 {actor} 核准，進入下一關卡。",
            url,
            "info",
        )
    elif action in {"finance_approve", "pay", "return", "reject"}:
        level = "success" if action in {"finance_approve", "pay"} else "danger"
        title = {
            "finance_approve": "核銷單已核准",
            "pay": "核銷單已撥款",
            "return": "核銷單被退回修改",
            "reject": "核銷單被駁回",
        }[action]
        notify(
            expense.applicant,
            title,
            f"{label}：{comment}" if comment else f"{label} 狀態已更新。",
            url,
            level,
        )


@retry_on_locked
def transition(
    *,
    expense_id: int,
    action: str,
    actor: User,
    comment: str = "",
    expected_version: int | None = None,
    request=None,
) -> Expense:

    if action not in ACTION_TARGET and action != "manager_approve":
        raise ValidationError("未知的簽核動作。")
    with transaction.atomic():
        expense = (
            Expense.objects.select_related("project", "applicant", "department")
            .filter(pk=expense_id)
            .first()
        )
        if expense is None:
            raise ValidationError("找不到核銷單。")
        if not can_act(actor, expense, action):
            raise PermissionDenied("您沒有執行此動作的權限。")
        if action in {"return", "reject"} and not comment.strip():
            raise ValidationError("退回或駁回必須填寫意見。")
        if action == "submit" and expense.total_amount <= 0:
            raise ValidationError("核銷單尚無發票或金額為 0，無法送審。")
        if expected_version is not None and expense.version != expected_version:
            raise ConcurrentModification("資料已被其他人更新，請重新載入後再試。")
        if action == "manager_approve":
            threshold = SystemSetting.load().approval_threshold
            target_status = (
                Expense.Status.EXEC_REVIEW
                if expense.total_amount > threshold
                else Expense.Status.FINANCE_REVIEW
            )
        else:
            target_status = ACTION_TARGET[action]

        budget_warning = None
        if action in {"submit", "finance_approve"}:
            budget_warning = check_project_budget(expense.project, expense.total_amount)

        update_fields: dict[str, Any] = {
            "status": target_status,
            "version": F("version") + 1,
            "updated_at": timezone.now(),
        }
        if action == "submit":
            update_fields["submitted_at"] = timezone.now()
        if action == "finance_approve":
            update_fields["approved_at"] = timezone.now()
        if action == "pay":
            update_fields["paid_at"] = timezone.now()

        old_status = expense.status
        old_version = expense.version
        updated = Expense.objects.filter(
            pk=expense.pk, version=expense.version, status=expense.status
        ).update(**update_fields)
        if not updated:
            raise ConcurrentModification("資料已被其他人更新，請重新載入後再試。")

        log_action(
            action=AuditLog.Action.UPDATE,
            user=actor,
            model_label="expenses.Expense",
            object_id=expense.pk,
            object_repr=str(expense),
            changes={
                "status": {"before": old_status, "after": target_status},
                "version": {"before": old_version, "after": old_version + 1},
            },
            request=request,
        )

        if action == "finance_approve" and expense.project_id:
            Project.objects.filter(pk=expense.project_id).update(
                spent_amount=F("spent_amount") + expense.total_amount
            )

        ApprovalLog.objects.create(
            expense=expense,
            actor=actor,
            action=action,
            from_status=expense.status,
            to_status=target_status,
            comment=comment.strip(),
            ip=get_client_ip(request) if request is not None else None,
        )
        expense.status = target_status
        expense.version += 1
        expense._budget_warning = budget_warning
        _notify_after_action(expense, action, actor, comment, target_status)

    transaction.on_commit(bump_dashboard_version)
    return expense


@retry_on_locked
def save_invoice(
    *,
    expense: Expense,
    invoice_form: Any,
    item_formset: Any,
    actor: User,
) -> Invoice:
    with transaction.atomic():
        invoice: Invoice = invoice_form.save(commit=False)
        invoice.expense = expense
        invoice.save()
        item_formset.instance = invoice
        item_formset.save()
        invoice.recalc_totals()
        expense.recalc_total()
    transaction.on_commit(bump_dashboard_version)
    return invoice


@retry_on_locked
def delete_invoice(*, invoice: Invoice) -> None:
    expense = invoice.expense
    with transaction.atomic():
        for attachment in invoice.attachments.all():
            attachment.delete()
        invoice.delete()
        expense.recalc_total()
    transaction.on_commit(bump_dashboard_version)


def save_attachment(*, invoice: Invoice, uploaded_file, user: User, info) -> InvoiceAttachment:

    attachment = InvoiceAttachment(
        invoice=invoice,
        original_name=(uploaded_file.name or "attachment")[:255],
        content_type=info.content_type,
        size=info.size,
        sha256=info.sha256,
        uploaded_by=user,
    )
    attachment.file.save(uploaded_file.name, uploaded_file, save=True)
    return attachment


def recalc_invoice(invoice: Invoice) -> Decimal:
    total = invoice.recalc_totals()
    invoice.expense.recalc_total()
    return total


def apply_filters(queryset: QuerySet[Expense], data: dict[str, Any]) -> QuerySet[Expense]:
    q = (data.get("q") or "").strip()
    if q:
        queryset = queryset.filter(
            Q(number__icontains=q)
            | Q(reason__icontains=q)
            | Q(applicant__username__icontains=q)
            | Q(applicant__first_name__icontains=q)
            | Q(applicant__last_name__icontains=q)
            | Q(invoices__invoice_no__icontains=q)
            | Q(invoices__seller_name__icontains=q)
        ).distinct()
    if data.get("date_from"):
        queryset = queryset.filter(apply_date__gte=data["date_from"])
    if data.get("date_to"):
        queryset = queryset.filter(apply_date__lte=data["date_to"])
    if data.get("department"):
        queryset = queryset.filter(department=data["department"])
    if data.get("project"):
        queryset = queryset.filter(project=data["project"])
    if data.get("project_type"):
        queryset = queryset.filter(project_type=data["project_type"])
    if data.get("category"):
        queryset = queryset.filter(invoices__items__category=data["category"]).distinct()
    if data.get("vendor"):
        queryset = queryset.filter(invoices__seller_name__icontains=data["vendor"]).distinct()
    if data.get("status"):
        queryset = queryset.filter(status=data["status"])
    if data.get("amount_min") is not None:
        queryset = queryset.filter(total_amount__gte=data["amount_min"])
    if data.get("amount_max") is not None:
        queryset = queryset.filter(total_amount__lte=data["amount_max"])
    if data.get("invoice_no"):
        queryset = queryset.filter(invoices__invoice_no__icontains=data["invoice_no"]).distinct()
    if data.get("applicant"):
        queryset = queryset.filter(applicant=data["applicant"])
    sort = data.get("sort") or "-apply_date"
    if sort not in SORT_WHITELIST:
        sort = "-apply_date"
    return queryset.order_by(sort, "-id")


def expense_totals(queryset: QuerySet[Expense]) -> Decimal:
    return quantize_money(queryset.aggregate(value=Sum("total_amount"))["value"] or 0)


@retry_on_locked
def delete_expense(*, expense: Expense) -> None:
    with transaction.atomic():
        for invoice in expense.invoices.prefetch_related("attachments"):
            for attachment in invoice.attachments.all():
                attachment.delete()
        expense.delete()
    transaction.on_commit(bump_dashboard_version)
