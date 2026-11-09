from __future__ import annotations

import pytest

from apps.audit.models import AuditLog
from apps.expenses.services import transition

pytestmark = pytest.mark.django_db


def test_expense_creation_and_transition_are_audited(
    employee, manager, department, expense_factory
):
    expense = expense_factory(employee, department)
    assert AuditLog.objects.filter(
        action=AuditLog.Action.CREATE,
        model_label="expenses.Expense",
        object_id=str(expense.pk),
    ).exists()

    transition(expense_id=expense.pk, action="submit", actor=employee)
    assert AuditLog.objects.filter(
        action=AuditLog.Action.UPDATE,
        model_label="expenses.Expense",
        object_id=str(expense.pk),
    ).exists()


def test_login_is_audited(client, employee):
    client.post(
        "/accounts/login/",
        {"username": employee.username, "password": "TestPass123!"},
    )
    assert AuditLog.objects.filter(
        action=AuditLog.Action.LOGIN, username=employee.username
    ).exists()
