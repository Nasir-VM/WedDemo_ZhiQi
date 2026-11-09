from __future__ import annotations

import pytest
from django.core.exceptions import PermissionDenied

from apps.expenses.permissions import can_act, can_edit_expense, visible_expenses
from apps.expenses.services import transition

pytestmark = pytest.mark.django_db


def test_employee_sees_only_own(employee, other_employee, department, expense_factory):
    own = expense_factory(employee, department)
    expense_factory(other_employee, department)
    assert list(visible_expenses(employee)) == [own]


def test_manager_sees_department(
    manager, employee, other_employee, department, other_department, expense_factory
):
    own_dept = expense_factory(employee, department)
    other_dept = expense_factory(other_employee, other_department)
    visible = set(visible_expenses(manager))
    assert own_dept in visible
    assert other_dept not in visible


def test_finance_and_auditor_see_all(finance, auditor, employee, department, expense_factory):
    expense = expense_factory(employee, department)
    assert expense in visible_expenses(finance)
    assert expense in visible_expenses(auditor)


def test_auditor_is_readonly(auditor, employee, department, expense_factory):
    expense = expense_factory(employee, department)
    assert not auditor.can_create_expense
    assert not can_edit_expense(auditor, expense)
    assert not can_act(auditor, expense, "submit")


def test_manager_cannot_approve_own(manager, department, expense_factory):
    expense = expense_factory(manager, department)
    transition(expense_id=expense.pk, action="submit", actor=manager)
    with pytest.raises(PermissionDenied):
        transition(expense_id=expense.pk, action="manager_approve", actor=manager)


def test_manager_cannot_approve_other_department(
    manager, employee, other_department, expense_factory
):
    expense = expense_factory(employee, other_department)
    transition(expense_id=expense.pk, action="submit", actor=employee)
    with pytest.raises(PermissionDenied):
        transition(expense_id=expense.pk, action="manager_approve", actor=manager)


def test_employee_cannot_approve(employee, other_employee, department, expense_factory):
    expense = expense_factory(other_employee, department)
    transition(expense_id=expense.pk, action="submit", actor=other_employee)
    with pytest.raises(PermissionDenied):
        transition(expense_id=expense.pk, action="manager_approve", actor=employee)
