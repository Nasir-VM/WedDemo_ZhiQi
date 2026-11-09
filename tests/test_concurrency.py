from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pytest
from django.db import connections

from apps.accounts.models import User
from apps.expenses.models import Expense
from apps.expenses.services import create_expense

pytestmark = pytest.mark.django_db(transaction=True)


def _create_one(
    user_id: int, department_id: int, project_id: int, project_type_id: int, index: int
) -> str:
    try:
        user = User.objects.get(pk=user_id)
        expense = create_expense(
            applicant=user,
            data={
                "department_id": department_id,
                "project_id": project_id,
                "project_type_id": project_type_id,
                "apply_date": date(2026, 1, 15),
                "reason": f"concurrency-{index}",
            },
        )
        return expense.number
    finally:
        connections.close_all()


def test_concurrent_creation_has_unique_numbers(
    employee, department, project_factory, project_type
):
    project = project_factory(employee)
    total = 8
    with ThreadPoolExecutor(max_workers=4) as executor:
        numbers = list(
            executor.map(
                lambda index: _create_one(
                    employee.pk, department.pk, project.pk, project_type.pk, index
                ),
                range(total),
            )
        )
    assert len(numbers) == total
    assert len(set(numbers)) == total
    assert Expense.objects.filter(reason__startswith="concurrency-").count() == total
