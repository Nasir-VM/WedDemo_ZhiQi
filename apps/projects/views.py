from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.expenses.services import visible_expenses
from apps.projects.forms import ProjectForm
from apps.projects.models import Project


def _can_manage(user, project: Project | None = None) -> bool:
    if not user.is_authenticated or user.is_readonly:
        return False
    if user.can_manage_master:
        return True
    if user.role == "manager" and user.department_id:
        return project is None or project.department_id == user.department_id
    return False


def project_list(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    queryset = Project.objects.select_related("project_type", "department", "owner")
    status = request.GET.get("status", "").strip()
    q = request.GET.get("q", "").strip()
    if status:
        queryset = queryset.filter(status=status)
    if q:
        queryset = queryset.filter(name__icontains=q) | queryset.filter(code__icontains=q)
    projects = queryset.order_by("code")
    return render(
        request,
        "projects/list.html",
        {
            "projects": projects,
            "statuses": Project.Status.choices,
            "filters": {"status": status, "q": q},
            "can_manage": _can_manage(request.user),
        },
    )


def project_detail(request: HttpRequest, pk: int) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    project = get_object_or_404(
        Project.objects.select_related("project_type", "department", "owner"), pk=pk
    )
    expenses = (
        visible_expenses(request.user)
        .filter(project=project)
        .select_related("applicant", "department")
        .order_by("-apply_date")[:50]
    )
    totals = (
        visible_expenses(request.user).filter(project=project).aggregate(total=Sum("total_amount"))
    )
    return render(
        request,
        "projects/detail.html",
        {
            "project": project,
            "expenses": expenses,
            "visible_total": totals["total"] or 0,
            "can_manage": _can_manage(request.user, project),
        },
    )


def project_create(request: HttpRequest) -> HttpResponse:
    if not _can_manage(request.user):
        raise PermissionDenied
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        project = form.save()
        messages.success(request, f"計畫「{project}」已建立。")
        return redirect("projects:detail", pk=project.pk)
    return render(request, "projects/form.html", {"form": form, "is_create": True})


def project_update(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not _can_manage(request.user, project):
        raise PermissionDenied
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        project = form.save()
        messages.success(request, f"計畫「{project}」已更新。")
        return redirect("projects:detail", pk=project.pk)
    return render(
        request,
        "projects/form.html",
        {"form": form, "is_create": False, "project": project},
    )
