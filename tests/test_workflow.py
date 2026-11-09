from __future__ import annotations

from decimal import Decimal

import pytest
from django.core.exceptions import PermissionDenied, ValidationError

from apps.core.models import SystemSetting
from apps.expenses.models import Expense
from apps.expenses.services import (
    BudgetExceeded,
    ConcurrentModification,
    transition,
    update_expense,
)
from apps.projects.models import Project

pytestmark = pytest.mark.django_db


def test_full_workflow(employee, manager, finance, department, project_factory, expense_factory):
    project = project_factory(manager, budget=Decimal("100000"))
    expense = expense_factory(employee, department, project=project, amount=Decimal("1000"))

    transition(expense_id=expense.pk, action="submit", actor=employee)
    assert Expense.objects.get(pk=expense.pk).status == Expense.Status.SUBMITTED

    transition(expense_id=expense.pk, action="manager_approve", actor=manager)
    assert Expense.objects.get(pk=expense.pk).status == Expense.Status.FINANCE_REVIEW

    transition(expense_id=expense.pk, action="finance_approve", actor=finance)
    expense.refresh_from_db()
    assert expense.status == Expense.Status.APPROVED
    assert expense.approved_at is not None
    project.refresh_from_db()
    assert project.spent_amount == Decimal("1000")

    transition(expense_id=expense.pk, action="pay", actor=finance)
    expense.refresh_from_db()
    assert expense.status == Expense.Status.PAID
    assert expense.paid_at is not None
    assert expense.logs.count() == 4


def test_threshold_requires_exec_approval(
    employee, manager, admin, finance, department, project_factory, expense_factory
):
    setting = SystemSetting.load()
    setting.approval_threshold = Decimal("50000")
    setting.save()
    project = project_factory(manager, budget=Decimal("200000"))
    expense = expense_factory(employee, department, project=project, amount=Decimal("60000"))

    transition(expense_id=expense.pk, action="submit", actor=employee)
    transition(expense_id=expense.pk, action="manager_approve", actor=manager)
    assert Expense.objects.get(pk=expense.pk).status == Expense.Status.EXEC_REVIEW

    transition(expense_id=expense.pk, action="exec_approve", actor=admin)
    assert Expense.objects.get(pk=expense.pk).status == Expense.Status.FINANCE_REVIEW
    transition(expense_id=expense.pk, action="finance_approve", actor=finance)
    assert Expense.objects.get(pk=expense.pk).status == Expense.Status.APPROVED


def test_return_requires_comment_and_can_resubmit(employee, manager, department, expense_factory):
    expense = expense_factory(employee, department)
    transition(expense_id=expense.pk, action="submit", actor=employee)
    with pytest.raises(ValidationError):
        transition(expense_id=expense.pk, action="return", actor=manager, comment="  ")

    transition(expense_id=expense.pk, action="return", actor=manager, comment="補單據")
    assert Expense.objects.get(pk=expense.pk).status == Expense.Status.RETURNED

    transition(expense_id=expense.pk, action="submit", actor=employee)
    assert Expense.objects.get(pk=expense.pk).status == Expense.Status.SUBMITTED


def test_reject(employee, manager, department, expense_factory):
    expense = expense_factory(employee, department)
    transition(expense_id=expense.pk, action="submit", actor=employee)
    transition(expense_id=expense.pk, action="reject", actor=manager, comment="不符規定")
    assert Expense.objects.get(pk=expense.pk).status == Expense.Status.REJECTED


def test_claim_then_approve(employee, manager, department, expense_factory):
    expense = expense_factory(employee, department)
    transition(expense_id=expense.pk, action="submit", actor=employee)
    transition(expense_id=expense.pk, action="claim", actor=manager)
    assert Expense.objects.get(pk=expense.pk).status == Expense.Status.MANAGER_REVIEW
    transition(expense_id=expense.pk, action="manager_approve", actor=manager)
    assert Expense.objects.get(pk=expense.pk).status == Expense.Status.FINANCE_REVIEW


def test_budget_block(employee, manager, department, project_factory, expense_factory):
    project = project_factory(manager, budget=Decimal("100"), control=Project.BudgetControl.BLOCK)
    expense = expense_factory(employee, department, project=project, amount=Decimal("200"))
    with pytest.raises(BudgetExceeded):
        transition(expense_id=expense.pk, action="submit", actor=employee)
    assert Expense.objects.get(pk=expense.pk).status == Expense.Status.DRAFT


def test_budget_warn_allows_submit(employee, manager, department, project_factory, expense_factory):
    project = project_factory(manager, budget=Decimal("100"), control=Project.BudgetControl.WARN)
    expense = expense_factory(employee, department, project=project, amount=Decimal("200"))
    updated = transition(expense_id=expense.pk, action="submit", actor=employee)
    assert updated.status == Expense.Status.SUBMITTED
    assert getattr(updated, "_budget_warning", None)


def test_submit_zero_total_rejected(employee, department):
    expense = Expense.objects.create(
        applicant=employee, department=department, reason="空單", total_amount=0
    )
    with pytest.raises(ValidationError):
        transition(expense_id=expense.pk, action="submit", actor=employee)


def test_optimistic_lock(employee, department, expense_factory):
    expense = expense_factory(employee, department)
    with pytest.raises(ConcurrentModification):
        update_expense(
            expense=expense,
            expected_version=expense.version + 1,
            data={"reason": "新事由"},
            actor=employee,
        )
    old_version = expense.version
    updated = update_expense(
        expense=expense,
        expected_version=old_version,
        data={"reason": "新事由"},
        actor=employee,
    )
    assert updated.reason == "新事由"
    assert updated.version == old_version + 1


def test_cannot_edit_locked_expense(employee, department, expense_factory):
    expense = expense_factory(employee, department, status=Expense.Status.APPROVED)
    with pytest.raises(ValidationError):
        update_expense(
            expense=expense,
            expected_version=expense.version,
            data={"reason": "偷改"},
            actor=employee,
        )


def test_self_approval_forbidden(manager, department, expense_factory):
    expense = expense_factory(manager, department)
    transition(expense_id=expense.pk, action="submit", actor=manager)
    with pytest.raises(PermissionDenied):
        transition(expense_id=expense.pk, action="manager_approve", actor=manager)
