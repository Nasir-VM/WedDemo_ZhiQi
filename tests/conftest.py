from __future__ import annotations

import itertools
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache

from apps.accounts.models import Department
from apps.expenses.models import Expense, ExpenseCategory, Invoice, LineItem, Vendor
from apps.projects.models import Project, ProjectType

User = get_user_model()
_invoice_counter = itertools.count(1)
_user_counter = itertools.count(1)


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def department(db):
    return Department.objects.create(code="RD", name="研發部")


@pytest.fixture
def other_department(db):
    return Department.objects.create(code="SALES", name="業務部")


@pytest.fixture
def user_factory(db):
    def make(role=User.Role.EMPLOYEE, department=None, username=None, **kwargs):
        username = username or f"user{next(_user_counter)}"
        user = User.objects.create_user(
            username=username,
            password="TestPass123!",
            role=role,
            department=department,
            must_change_password=False,
            **kwargs,
        )
        return user

    return make


@pytest.fixture
def employee(user_factory, department):
    return user_factory(role=User.Role.EMPLOYEE, department=department)


@pytest.fixture
def other_employee(user_factory, department):
    return user_factory(role=User.Role.EMPLOYEE, department=department)


@pytest.fixture
def manager(user_factory, department):
    return user_factory(role=User.Role.MANAGER, department=department)


@pytest.fixture
def other_manager(user_factory, other_department):
    return user_factory(role=User.Role.MANAGER, department=other_department)


@pytest.fixture
def finance(user_factory, department):
    return user_factory(role=User.Role.FINANCE, department=department)


@pytest.fixture
def admin(user_factory):
    return user_factory(role=User.Role.ADMIN, is_staff=True, is_superuser=True)


@pytest.fixture
def auditor(user_factory):
    return user_factory(role=User.Role.AUDITOR)


@pytest.fixture
def project_type(db):
    obj, _ = ProjectType.objects.get_or_create(
        code="GENERAL", defaults={"name": "一般營運", "description": "日常營運支出"}
    )
    return obj


@pytest.fixture
def category(db):
    obj, _ = ExpenseCategory.objects.get_or_create(
        code="MEALS", defaults={"name": "餐飲", "description": "餐費與招待"}
    )
    return obj


@pytest.fixture
def project_factory(db, project_type, department):
    def make(owner, budget=Decimal("100000"), control=Project.BudgetControl.WARN, **kwargs):
        return Project.objects.create(
            code=kwargs.pop("code", f"P{next(_invoice_counter):04d}"),
            name=kwargs.pop("name", "測試計畫"),
            project_type=project_type,
            owner=owner,
            department=kwargs.pop("department", department),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            budget_total=budget,
            budget_control=control,
            **kwargs,
        )

    return make


@pytest.fixture
def expense_factory(db, category):
    def make(
        applicant,
        department,
        *,
        amount=Decimal("1000"),
        status=Expense.Status.DRAFT,
        project=None,
        project_type=None,
        reason="測試費用",
        invoice_no=None,
    ):
        expense = Expense.objects.create(
            applicant=applicant,
            department=department,
            project=project,
            project_type=project_type or (project.project_type if project else None),
            apply_date=date(2026, 1, 15),
            reason=reason,
            status=Expense.Status.DRAFT,
        )
        invoice = Invoice.objects.create(
            expense=expense,
            invoice_type=Invoice.InvoiceType.ELECTRONIC,
            invoice_no=invoice_no or f"AB{next(_invoice_counter):08d}",
            issue_date=date(2026, 1, 15),
            seller_name="測試廠商",
            seller_tax_id="04595257",
            tax_rate=Decimal("0"),
        )
        LineItem.objects.create(
            invoice=invoice,
            name="測試品項",
            quantity=Decimal("1"),
            unit_price=amount,
            category=category,
        )
        invoice.recalc_totals()
        expense.recalc_total()
        if status != Expense.Status.DRAFT:
            Expense.objects.filter(pk=expense.pk).update(status=status)
        return Expense.objects.get(pk=expense.pk)

    return make


@pytest.fixture
def vendor(db):
    return Vendor.objects.create(name="測試廠商", tax_id="04595257")
