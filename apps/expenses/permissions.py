from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.expenses.models import Expense


def visible_expenses(user) -> QuerySet[Expense]:

    queryset = Expense.objects.all()
    if not user.is_authenticated:
        return queryset.none()
    if user.can_view_all:
        return queryset
    if user.role == "manager" and user.department_id:
        return queryset.filter(department_id=user.department_id)
    return queryset.filter(applicant_id=user.id)


def can_view_expense(user, expense: Expense) -> bool:
    if not user.is_authenticated:
        return False
    if user.can_view_all:
        return True
    if user.role == "manager" and user.department_id:
        return expense.department_id == user.department_id
    return expense.applicant_id == user.id


REVIEW_STATUSES = {
    Expense.Status.SUBMITTED,
    Expense.Status.MANAGER_REVIEW,
    Expense.Status.EXEC_REVIEW,
    Expense.Status.FINANCE_REVIEW,
}


def is_department_manager(user, expense: Expense) -> bool:
    if user.is_admin_role:
        return True
    return (
        user.role == "manager"
        and user.department_id is not None
        and expense.department_id == user.department_id
    )


def can_act(user, expense: Expense, action: str) -> bool:
    if not user.is_authenticated or user.is_readonly:
        return False
    status = expense.status
    is_applicant = expense.applicant_id == user.id
    if action == "submit":
        return is_applicant and status in {Expense.Status.DRAFT, Expense.Status.RETURNED}
    if action == "claim":
        return (
            not is_applicant
            and is_department_manager(user, expense)
            and user.can_approve_manager
            and status == Expense.Status.SUBMITTED
        )
    if action == "manager_approve":
        return (
            not is_applicant
            and is_department_manager(user, expense)
            and user.can_approve_manager
            and status in {Expense.Status.SUBMITTED, Expense.Status.MANAGER_REVIEW}
        )
    if action == "exec_approve":
        return not is_applicant and user.can_approve_exec and status == Expense.Status.EXEC_REVIEW
    if action == "finance_approve":
        return (
            not is_applicant
            and user.can_approve_finance
            and status == Expense.Status.FINANCE_REVIEW
        )
    if action == "pay":
        return user.can_approve_finance and status == Expense.Status.APPROVED
    if action in {"return", "reject"}:
        if status not in REVIEW_STATUSES or is_applicant:
            return False
        if user.can_approve_finance:
            return True
        return is_department_manager(user, expense) and user.can_approve_manager
    return False


def can_edit_expense(user, expense: Expense) -> bool:
    return can_view_expense(user, expense) and expense.can_edit(user)


def can_delete_invoice(user, expense: Expense) -> bool:
    return can_edit_expense(user, expense)


def invoice_search_q(value: str) -> Q:
    return Q(invoices__invoice_no__icontains=value) | Q(invoices__seller_name__icontains=value)
