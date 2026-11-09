from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.core.cache import cache
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Department, User
from apps.core.cache import dashboard_version
from apps.core.models import SystemSetting
from apps.expenses.models import Expense, LineItem
from apps.expenses.permissions import REVIEW_STATUSES, visible_expenses
from apps.expenses.services import pending_review_count, review_statuses_for
from apps.projects.models import Project

FINAL_STATUSES = [Expense.Status.APPROVED, Expense.Status.PAID]


def shift_month(value: date, delta: int) -> date:
    index = value.year * 12 + (value.month - 1) + delta
    return date(index // 12, index % 12 + 1, 1)


def visible_projects(user: User):
    queryset = Project.objects.all()
    if user.can_view_all:
        return queryset
    if user.role == User.Role.MANAGER and user.department_id:
        return queryset.filter(department_id=user.department_id)
    return queryset.filter(Q(owner=user) | Q(expenses__applicant=user)).distinct()


def _expense_row(expense: Expense) -> dict:
    return {
        "id": expense.pk,
        "number": expense.number,
        "applicant": expense.applicant.get_full_name() or expense.applicant.username,
        "department": expense.department.name if expense.department_id else "",
        "total": float(expense.total_amount),
        "status": expense.status,
        "status_label": expense.get_status_display(),
        "url": reverse("expenses:detail", args=[expense.pk]),
        "updated_at": timezone.localtime(expense.updated_at).strftime("%m/%d %H:%M"),
    }


def _company_overview() -> dict:
    year = timezone.localdate().year
    key = f"company_overview:{year}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    final = Expense.objects.filter(status__in=FINAL_STATUSES, apply_date__year=year)
    data = {
        "year": year,
        "year_total": float(final.aggregate(value=Sum("total_amount"))["value"] or 0),
        "departments": Department.objects.filter(is_active=True).count(),
        "employees": User.objects.filter(is_active=True).count(),
        "pending": Expense.objects.filter(status__in=REVIEW_STATUSES).count(),
        "approved": Expense.objects.filter(status=Expense.Status.APPROVED).count(),
    }
    cache.set(key, data, 120)
    return data


def dashboard_data(user: User) -> dict:
    setting = SystemSetting.load()
    cache_key = (
        f"dashboard:{user.pk}:{dashboard_version()}:{user.role}:{user.department_id}:"
        f"{timezone.localdate().isoformat()}"
    )
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    today = timezone.localdate()
    month_start = today.replace(day=1)
    scoped = visible_expenses(user)
    final = scoped.filter(status__in=FINAL_STATUSES)

    month_total = final.filter(apply_date__gte=month_start).aggregate(value=Sum("total_amount"))[
        "value"
    ] or Decimal("0")
    in_review = scoped.filter(status__in=REVIEW_STATUSES).count()
    approved_unpaid = scoped.filter(status=Expense.Status.APPROVED).aggregate(
        value=Sum("total_amount")
    )["value"] or Decimal("0")

    projects = list(visible_projects(user))
    budget_total = sum((project.budget_total for project in projects), Decimal("0"))
    spent_total = sum((project.spent_amount for project in projects), Decimal("0"))
    budget_rate = float(spent_total / budget_total * 100) if budget_total else 0.0

    start = shift_month(today.replace(day=1), -11)
    trend_rows = (
        final.filter(apply_date__gte=start)
        .annotate(month=TruncMonth("apply_date"))
        .values("month")
        .annotate(total=Sum("total_amount"))
        .order_by("month")
    )
    trend_map = {
        row["month"].strftime("%Y-%m"): float(row["total"]) for row in trend_rows if row["month"]
    }
    trend_labels: list[str] = []
    trend_values: list[float] = []
    for offset in range(12):
        month = shift_month(start, offset)
        key = month.strftime("%Y-%m")
        trend_labels.append(f"{month.month}月")
        trend_values.append(round(trend_map.get(key, 0.0), 2))

    dept_rows = (
        final.values("department__name").annotate(total=Sum("total_amount")).order_by("-total")[:8]
    )
    category_rows = (
        LineItem.objects.filter(invoice__expense__in=final)
        .values("category__name")
        .annotate(total=Sum("subtotal"))
        .order_by("-total")[:8]
    )
    top_projects = sorted(projects, key=lambda p: p.budget_total, reverse=True)[:8]

    latest = [
        _expense_row(expense)
        for expense in scoped.select_related("applicant", "department").order_by("-updated_at")[:8]
    ]

    todo_statuses = review_statuses_for(user)
    if todo_statuses:
        todo_qs = scoped.filter(status__in=todo_statuses).exclude(applicant=user)
    else:
        todo_qs = scoped.filter(status__in=[Expense.Status.DRAFT, Expense.Status.RETURNED])
    todos = [
        _expense_row(expense)
        for expense in todo_qs.select_related("applicant", "department").order_by("-updated_at")[:8]
    ]

    warnings = [
        {
            "code": project.code,
            "name": project.name,
            "rate": round(project.execution_rate, 1),
            "budget": float(project.budget_total),
            "spent": float(project.spent_amount),
            "over": project.is_over_budget,
            "url": reverse("projects:detail", args=[project.pk]),
        }
        for project in projects
        if project.budget_total and project.execution_rate >= 90
    ]
    warnings.sort(key=lambda item: item["rate"], reverse=True)

    data = {
        "kpis": {
            "month_total": float(month_total),
            "pending": pending_review_count(user),
            "in_review": in_review,
            "approved_unpaid": float(approved_unpaid),
            "budget_rate": round(budget_rate, 1),
            "budget_total": float(budget_total),
            "spent_total": float(spent_total),
        },
        "trend": {"labels": trend_labels, "values": trend_values},
        "department_share": {
            "labels": [row["department__name"] or "未指定" for row in dept_rows],
            "values": [float(row["total"]) for row in dept_rows],
        },
        "category_share": {
            "labels": [row["category__name"] for row in category_rows],
            "values": [float(row["total"]) for row in category_rows],
        },
        "project_chart": {
            "labels": [project.code for project in top_projects],
            "budget": [float(project.budget_total) for project in top_projects],
            "spent": [float(project.spent_amount) for project in top_projects],
        },
        "latest": latest,
        "todos": todos,
        "warnings": warnings[:6],
        "company": _company_overview(),
        "announcement": setting.announcement,
        "as_of": timezone.localtime().strftime("%Y-%m-%d %H:%M"),
    }
    cache.set(cache_key, data, setting.dashboard_cache_seconds)
    return data


def report_data(
    user: User, *, year: int, quarter: int | None = None, month: int | None = None
) -> dict:
    scoped = visible_expenses(user)
    queryset = scoped.filter(status__in=FINAL_STATUSES, apply_date__year=year)
    if month:
        queryset = queryset.filter(apply_date__month=month)
    if quarter:
        queryset = queryset.filter(apply_date__quarter=quarter)

    totals = queryset.aggregate(total=Sum("total_amount"), count=Count("id"))
    monthly_rows = (
        queryset.annotate(month=TruncMonth("apply_date"))
        .values("month")
        .annotate(total=Sum("total_amount"), count=Count("id"))
        .order_by("month")
    )
    monthly_map = {row["month"].strftime("%Y-%m"): row for row in monthly_rows if row["month"]}
    month_labels: list[str] = []
    month_values: list[float] = []
    for index in range(1, 13):
        key = f"{year:04d}-{index:02d}"
        month_labels.append(f"{index}月")
        month_values.append(float(monthly_map.get(key, {}).get("total") or 0))

    by_department = list(
        queryset.values("department__name")
        .annotate(total=Sum("total_amount"), count=Count("id"))
        .order_by("-total")
    )
    by_project = list(
        queryset.values("project__code", "project__name")
        .annotate(total=Sum("total_amount"), count=Count("id"))
        .order_by("-total")
    )
    by_category = list(
        LineItem.objects.filter(invoice__expense__in=queryset)
        .values("category__name")
        .annotate(total=Sum("subtotal"))
        .order_by("-total")
    )
    by_applicant = list(
        queryset.values("applicant__username", "applicant__first_name", "applicant__last_name")
        .annotate(total=Sum("total_amount"), count=Count("id"))
        .order_by("-total")[:20]
    )
    status_rows = list(
        scoped.filter(apply_date__year=year)
        .values("status")
        .annotate(total=Sum("total_amount"), count=Count("id"))
        .order_by("status")
    )
    status_labels = dict(Expense.Status.choices)
    for row in status_rows:
        row["label"] = status_labels.get(row["status"], row["status"])

    matrix_rows = list(
        LineItem.objects.filter(invoice__expense__in=queryset)
        .values("invoice__expense__department__name", "category__name")
        .annotate(total=Sum("subtotal"))
    )
    departments = sorted(
        {row["invoice__expense__department__name"] or "未指定" for row in matrix_rows}
    )
    categories = sorted({row["category__name"] for row in matrix_rows})
    matrix: dict[str, dict[str, float]] = {dept: {} for dept in departments}
    for row in matrix_rows:
        dept = row["invoice__expense__department__name"] or "未指定"
        matrix[dept][row["category__name"]] = float(row["total"])

    projects = [
        {
            "code": project.code,
            "name": project.name,
            "budget": float(project.budget_total),
            "spent": float(project.spent_amount),
            "rate": round(project.execution_rate, 1),
            "url": reverse("projects:detail", args=[project.pk]),
        }
        for project in visible_projects(user)
    ]
    projects.sort(key=lambda item: item["rate"], reverse=True)

    return {
        "year": year,
        "quarter": quarter,
        "month": month,
        "totals": {
            "total": float(totals["total"] or 0),
            "count": totals["count"] or 0,
        },
        "monthly": {"labels": month_labels, "values": month_values},
        "by_department": by_department,
        "by_project": by_project,
        "by_category": by_category,
        "by_applicant": by_applicant,
        "status_rows": status_rows,
        "matrix": {"departments": departments, "categories": categories, "values": matrix},
        "projects": projects,
    }
