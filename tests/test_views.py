from __future__ import annotations

import pytest
from django.urls import reverse

from apps.expenses.models import Expense

pytestmark = pytest.mark.django_db


def test_login_required(client):
    response = client.get(reverse("dashboard:index"))
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


def test_dashboard_and_lists_render(client, employee):
    client.force_login(employee)
    for url in (
        reverse("dashboard:index"),
        reverse("expenses:list"),
        reverse("reports:index"),
        reverse("projects:list"),
        reverse("notifications:list"),
        reverse("accounts:profile"),
    ):
        response = client.get(url)
        assert response.status_code == 200, url


def test_expense_create_view(client, employee, department, project_type, project_factory):
    project = project_factory(employee)
    client.force_login(employee)
    response = client.post(
        reverse("expenses:create"),
        {
            "department": department.pk,
            "project_type": project_type.pk,
            "project": project.pk,
            "apply_date": "2026-01-15",
            "reason": "視圖建立測試",
        },
    )
    assert response.status_code == 302
    expense = Expense.objects.get(reason="視圖建立測試")
    assert expense.applicant == employee
    assert expense.number.startswith("志-")


def test_expense_detail_and_action(client, employee, manager, department, expense_factory):
    expense = expense_factory(employee, department)
    client.force_login(employee)
    detail = client.get(reverse("expenses:detail", args=[expense.pk]))
    assert detail.status_code == 200
    assert expense.number.encode() in detail.content

    response = client.post(
        reverse("expenses:action", args=[expense.pk]),
        {"action": "submit", "version": expense.version},
    )
    assert response.status_code == 302
    expense.refresh_from_db()
    assert expense.status == Expense.Status.SUBMITTED


def test_export_csv(client, employee, department, expense_factory):
    expense = expense_factory(employee, department, reason="=HYPERLINK(惡意)")
    client.force_login(employee)
    response = client.get(reverse("expenses:export"), {"format": "csv"})
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    body = response.content.decode("utf-8-sig")
    assert expense.number in body
    assert "'=HYPERLINK(惡意)" in body


def test_export_xlsx(client, employee, department, expense_factory):
    expense_factory(employee, department)
    client.force_login(employee)
    response = client.get(reverse("expenses:export"), {"format": "xlsx"})
    assert response.status_code == 200
    assert response.content.startswith(b"PK")


def test_audit_permissions(client, admin, employee):
    client.force_login(employee)
    assert client.get(reverse("audit:list")).status_code == 403
    client.force_login(admin)
    response = client.get(reverse("audit:list"))
    assert response.status_code == 200
    assert "稽核日誌".encode() in response.content


def test_master_pages(client, admin):
    client.force_login(admin)
    assert client.get(reverse("master:index")).status_code == 200
    assert client.get(reverse("master:list", args=["categories"])).status_code == 200


def test_employee_cannot_open_master(client, employee):
    client.force_login(employee)
    assert client.get(reverse("master:index")).status_code == 200
    assert client.get(reverse("master:list", args=["categories"])).status_code == 403


def test_logout_requires_post(client, employee):
    client.force_login(employee)
    assert client.get(reverse("accounts:logout")).status_code == 403
    assert client.post(reverse("accounts:logout")).status_code == 302
