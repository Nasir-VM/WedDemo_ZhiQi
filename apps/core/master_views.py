from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import ProtectedError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import CostCenter, Department
from apps.core.forms import (
    CostCenterForm,
    DepartmentForm,
    ExpenseCategoryForm,
    ProjectTypeForm,
    VendorForm,
)
from apps.expenses.models import ExpenseCategory, Vendor
from apps.projects.models import ProjectType

MASTER_CONFIG: dict[str, dict[str, Any]] = {
    "departments": {
        "model": Department,
        "form": DepartmentForm,
        "title": "部門",
        "admin_only": True,
        "columns": [("code", "代碼"), ("name", "名稱"), ("parent", "上層部門")],
    },
    "cost-centers": {
        "model": CostCenter,
        "form": CostCenterForm,
        "title": "成本中心",
        "admin_only": True,
        "columns": [("code", "代碼"), ("name", "名稱"), ("department", "所屬部門")],
    },
    "vendors": {
        "model": Vendor,
        "form": VendorForm,
        "title": "供應商／廠商",
        "admin_only": False,
        "columns": [("name", "名稱"), ("tax_id", "統一編號"), ("contact_person", "聯絡人")],
    },
    "categories": {
        "model": ExpenseCategory,
        "form": ExpenseCategoryForm,
        "title": "費用科目",
        "admin_only": False,
        "columns": [("code", "代碼"), ("name", "名稱")],
    },
    "project-types": {
        "model": ProjectType,
        "form": ProjectTypeForm,
        "title": "計畫類型",
        "admin_only": False,
        "columns": [("code", "代碼"), ("name", "名稱")],
    },
}


def _config(kind: str) -> dict[str, Any]:
    if kind not in MASTER_CONFIG:
        raise PermissionDenied("未知的基礎資料類型。")
    return MASTER_CONFIG[kind]


def _guard(request: HttpRequest, config: dict[str, Any]) -> None:
    if not request.user.is_authenticated:
        raise PermissionDenied
    if config["admin_only"]:
        if not request.user.can_manage_org:
            raise PermissionDenied("僅系統管理員可維護此資料。")
    elif not request.user.can_manage_master:
        raise PermissionDenied("您沒有維護基礎資料的權限。")


def master_index(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    items = [
        {"kind": kind, "title": config["title"]}
        for kind, config in MASTER_CONFIG.items()
        if (request.user.can_manage_org if config["admin_only"] else request.user.can_manage_master)
    ]
    return render(request, "master/index.html", {"items": items})


def master_list(request: HttpRequest, kind: str) -> HttpResponse:
    config = _config(kind)
    _guard(request, config)
    queryset = config["model"].objects.all()
    if kind in {"departments", "cost-centers"}:
        queryset = queryset.select_related("parent", "department")
    rows = []
    for obj in queryset:
        cells = []
        for field, _label in config["columns"]:
            value = getattr(obj, field, "")
            cells.append(str(value) if value not in (None, "") else "—")
        rows.append({"obj": obj, "cells": cells})
    return render(
        request,
        "master/list.html",
        {
            "kind": kind,
            "config": config,
            "rows": rows,
            "columns": config["columns"],
        },
    )


def master_create(request: HttpRequest, kind: str) -> HttpResponse:
    config = _config(kind)
    _guard(request, config)
    form = config["form"](request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        messages.success(request, f"{config['title']}「{obj}」已新增。")
        return redirect("master:list", kind=kind)
    return render(
        request,
        "master/form.html",
        {"kind": kind, "config": config, "form": form, "is_create": True},
    )


def master_update(request: HttpRequest, kind: str, pk: int) -> HttpResponse:
    config = _config(kind)
    _guard(request, config)
    obj = get_object_or_404(config["model"], pk=pk)
    form = config["form"](request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        messages.success(request, f"{config['title']}「{obj}」已更新。")
        return redirect("master:list", kind=kind)
    return render(
        request,
        "master/form.html",
        {"kind": kind, "config": config, "form": form, "is_create": False, "object": obj},
    )


def master_delete(request: HttpRequest, kind: str, pk: int) -> HttpResponse:
    config = _config(kind)
    _guard(request, config)
    if request.method != "POST":
        raise PermissionDenied("請以 POST 刪除。")
    obj = get_object_or_404(config["model"], pk=pk)
    try:
        obj.delete()
        messages.success(request, f"{config['title']}「{obj}」已刪除。")
    except ProtectedError:
        messages.error(request, "此資料已被引用，無法刪除；請改為停用。")
    return redirect("master:list", kind=kind)
