from __future__ import annotations

import json
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.audit.services import log_export
from apps.core.models import SystemSetting
from apps.core.ratelimit import rate_limit
from apps.expenses.analytics import report_data
from apps.expenses.exports import build_csv_response, build_xlsx_response
from apps.expenses.forms import (
    AttachmentForm,
    ExpenseFilterForm,
    ExpenseForm,
    InvoiceForm,
    LineItemFormSet,
)
from apps.expenses.models import Invoice, InvoiceAttachment
from apps.expenses.permissions import can_act, can_edit_expense, can_view_expense, visible_expenses
from apps.expenses.services import (
    BudgetExceeded,
    ConcurrentModification,
    apply_filters,
    create_expense,
    delete_expense,
    delete_invoice,
    expense_totals,
    save_attachment,
    save_invoice,
    transition,
    update_expense,
)
from apps.expenses.uploads import inspect_upload

ACTION_LABELS = {
    "submit": "送審",
    "claim": "接手審核",
    "manager_approve": "主管核准",
    "exec_approve": "上層加簽核准",
    "finance_approve": "財務核准",
    "pay": "標記已撥款",
    "return": "退回修改",
    "reject": "駁回",
}


def _parse_version(raw: str | None) -> int | None:
    try:
        return int(raw) if raw not in (None, "") else None
    except (TypeError, ValueError):
        return None


@login_required
def expense_list(request: HttpRequest) -> HttpResponse:
    form = ExpenseFilterForm(request.GET or None)
    data: dict[str, Any] = form.cleaned_data if form.is_valid() else {}
    queryset = visible_expenses(request.user).select_related(
        "applicant", "department", "project", "project_type"
    )
    queryset = apply_filters(queryset, data)
    total_amount = expense_totals(queryset)
    try:
        page_size = int(data.get("page_size") or 20)
    except (TypeError, ValueError):
        page_size = 20
    if page_size not in {20, 50, 100}:
        page_size = 20
    paginator = Paginator(queryset, page_size)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "expenses/list.html",
        {
            "form": form,
            "page": page,
            "total_amount": total_amount,
            "total_count": paginator.count,
            "page_size": page_size,
            "can_create": request.user.can_create_expense,
        },
    )


@login_required
def expense_detail(request: HttpRequest, pk: int) -> HttpResponse:
    expense = get_object_or_404(
        visible_expenses(request.user)
        .select_related("applicant", "department", "project", "project_type")
        .prefetch_related("invoices__items__category", "invoices__attachments", "logs__actor"),
        pk=pk,
    )
    available_actions = {action: can_act(request.user, expense, action) for action in ACTION_LABELS}
    return render(
        request,
        "expenses/detail.html",
        {
            "expense": expense,
            "available_actions": available_actions,
            "has_actions": any(available_actions.values()),
            "action_labels": ACTION_LABELS,
            "can_edit": can_edit_expense(request.user, expense),
            "attachment_form": AttachmentForm(),
        },
    )


@login_required
def expense_create(request: HttpRequest) -> HttpResponse:
    if not request.user.can_create_expense:
        raise PermissionDenied("您的角色為唯讀，無法建立核銷單。")
    initial = {
        "department": request.user.department_id,
        "apply_date": timezone.localdate(),
        "project_type": None,
    }
    form = ExpenseForm(request.POST or None, user=request.user, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            expense = create_expense(applicant=request.user, data=form.cleaned_data)
        except ValidationError as exc:
            form.add_error(None, exc.messages[0])
        else:
            messages.success(request, f"核銷單 {expense.number} 已建立，請新增發票與品項。")
            return redirect("expenses:detail", pk=expense.pk)
    return render(request, "expenses/form.html", {"form": form, "is_create": True})


@login_required
def expense_update(request: HttpRequest, pk: int) -> HttpResponse:
    expense = get_object_or_404(visible_expenses(request.user), pk=pk)
    if not can_edit_expense(request.user, expense):
        messages.error(request, "此核銷單目前不可編輯（已鎖定或無權限）。")
        return redirect("expenses:detail", pk=expense.pk)
    form = ExpenseForm(request.POST or None, instance=expense, user=request.user)
    if request.method == "POST" and form.is_valid():
        expected = _parse_version(request.POST.get("version"))
        if expected is None:
            expected = expense.version
        data = {
            "department_id": form.cleaned_data["department"].pk,
            "project_type_id": (
                form.cleaned_data["project_type"].pk if form.cleaned_data["project_type"] else None
            ),
            "project_id": form.cleaned_data["project"].pk if form.cleaned_data["project"] else None,
            "apply_date": form.cleaned_data["apply_date"],
            "reason": form.cleaned_data["reason"],
        }
        try:
            update_expense(
                expense=expense,
                expected_version=expected,
                data=data,
                actor=request.user,
            )
        except ConcurrentModification:
            messages.error(request, "資料已被其他人更新，請重新載入後再修改。")
            return redirect("expenses:update", pk=expense.pk)
        except ValidationError as exc:
            form.add_error(None, exc.messages[0])
        else:
            messages.success(request, "核銷單資料已更新。")
            return redirect("expenses:detail", pk=expense.pk)
    return render(
        request,
        "expenses/form.html",
        {"form": form, "is_create": False, "expense": expense},
    )


@login_required
def expense_delete(request: HttpRequest, pk: int) -> HttpResponse:
    expense = get_object_or_404(visible_expenses(request.user), pk=pk)
    if request.method != "POST":
        raise PermissionDenied("請以 POST 刪除。")
    if not can_edit_expense(request.user, expense):
        raise PermissionDenied("此核銷單不可刪除。")
    number = expense.number
    delete_expense(expense=expense)
    messages.success(request, f"核銷單 {number} 已刪除。")
    return redirect("expenses:list")


@login_required
def invoice_create(request: HttpRequest, pk: int) -> HttpResponse:
    expense = get_object_or_404(visible_expenses(request.user).select_related("department"), pk=pk)
    if not can_edit_expense(request.user, expense):
        raise PermissionDenied("此核銷單目前不可新增發票。")
    invoice = Invoice(
        expense=expense,
        issue_date=expense.apply_date,
        tax_rate=SystemSetting.load().default_tax_rate,
    )
    form = InvoiceForm(request.POST or None, request.FILES or None, instance=invoice)
    formset = LineItemFormSet(request.POST or None, instance=invoice, prefix="items")
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        saved = save_invoice(
            expense=expense, invoice_form=form, item_formset=formset, actor=request.user
        )
        upload = form.cleaned_data.get("attachment")
        if upload and form.upload_info is not None:
            try:
                save_attachment(
                    invoice=saved, uploaded_file=upload, user=request.user, info=form.upload_info
                )
            except Exception:
                messages.warning(request, "發票已儲存，但附件上傳失敗，請稍後補上。")
        messages.success(request, "發票與品項已新增，總金額已重新計算。")
        return redirect("expenses:detail", pk=expense.pk)
    return render(
        request,
        "expenses/invoice_form.html",
        {"expense": expense, "form": form, "formset": formset, "is_create": True},
    )


@login_required
def invoice_update(request: HttpRequest, pk: int) -> HttpResponse:
    invoice = get_object_or_404(Invoice.objects.select_related("expense"), pk=pk)
    expense = invoice.expense
    if not can_view_expense(request.user, expense) or not can_edit_expense(request.user, expense):
        raise PermissionDenied("此發票目前不可編輯。")
    form = InvoiceForm(request.POST or None, request.FILES or None, instance=invoice)
    formset = LineItemFormSet(request.POST or None, instance=invoice, prefix="items")
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        saved = save_invoice(
            expense=expense, invoice_form=form, item_formset=formset, actor=request.user
        )
        upload = form.cleaned_data.get("attachment")
        if upload and form.upload_info is not None:
            save_attachment(
                invoice=saved, uploaded_file=upload, user=request.user, info=form.upload_info
            )
        messages.success(request, "發票已更新。")
        return redirect("expenses:detail", pk=expense.pk)
    return render(
        request,
        "expenses/invoice_form.html",
        {
            "expense": expense,
            "form": form,
            "formset": formset,
            "is_create": False,
            "invoice": invoice,
        },
    )


@login_required
def invoice_delete(request: HttpRequest, pk: int) -> HttpResponse:
    invoice = get_object_or_404(Invoice.objects.select_related("expense"), pk=pk)
    expense = invoice.expense
    if request.method != "POST":
        raise PermissionDenied("請以 POST 刪除。")
    if not can_edit_expense(request.user, expense):
        raise PermissionDenied("此發票目前不可刪除。")
    delete_invoice(invoice=invoice)
    messages.success(request, "發票已刪除，總金額已重新計算。")
    return redirect("expenses:detail", pk=expense.pk)


@login_required
@require_POST
@rate_limit(key="user", rate="120/m")
def expense_action(request: HttpRequest, pk: int) -> HttpResponse:
    expense = get_object_or_404(visible_expenses(request.user), pk=pk)
    action = request.POST.get("action", "")
    if action not in ACTION_LABELS:
        raise PermissionDenied("未知的簽核動作。")
    comment = request.POST.get("comment", "")
    expected = _parse_version(request.POST.get("version"))
    try:
        updated = transition(
            expense_id=expense.pk,
            action=action,
            actor=request.user,
            comment=comment,
            expected_version=expected,
            request=request,
        )
    except BudgetExceeded as exc:
        messages.error(request, f"預算控管阻擋：{exc}")
    except ConcurrentModification:
        messages.error(request, "資料已被其他人更新，請重新載入後再操作。")
    except ValidationError as exc:
        messages.error(request, exc.messages[0])
    else:
        messages.success(
            request,
            f"已完成「{ACTION_LABELS[action]}」，目前狀態：{updated.get_status_display()}。",
        )
        warning = getattr(updated, "_budget_warning", None)
        if warning:
            messages.warning(request, f"預算警示：{warning}")
    return redirect("expenses:detail", pk=expense.pk)


@login_required
@require_POST
@rate_limit(key="user", rate="30/h")
def attachment_upload(request: HttpRequest, pk: int) -> HttpResponse:
    invoice = get_object_or_404(Invoice.objects.select_related("expense"), pk=pk)
    if not can_edit_expense(request.user, invoice.expense):
        raise PermissionDenied("此發票目前不可上傳附件。")
    form = AttachmentForm(request.POST, request.FILES)
    if form.is_valid():
        upload = form.cleaned_data["file"]
        try:
            info = inspect_upload(upload)
            save_attachment(invoice=invoice, uploaded_file=upload, user=request.user, info=info)
        except ValidationError as exc:
            messages.error(request, exc.messages[0])
        else:
            messages.success(request, "附件已上傳。")
    else:
        messages.error(request, "請選擇有效的附件檔案。")
    return redirect("expenses:detail", pk=invoice.expense_id)


@login_required
def attachment_download(request: HttpRequest, pk: int) -> HttpResponse:
    attachment = get_object_or_404(
        InvoiceAttachment.objects.select_related("invoice__expense"), pk=pk
    )
    if not can_view_expense(request.user, attachment.invoice.expense):
        raise PermissionDenied("您無權存取此附件。")
    if not attachment.file:
        raise Http404("附件不存在。")
    try:
        handle = attachment.file.open("rb")
    except FileNotFoundError as exc:
        raise Http404("附件檔案遺失。") from exc
    response = FileResponse(
        handle,
        content_type=attachment.content_type,
        as_attachment=request.GET.get("download") == "1",
        filename=attachment.original_name,
    )
    response["Cache-Control"] = "private, no-store, max-age=0"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@login_required
@rate_limit(key="user", rate="10/h")
def export_expenses(request: HttpRequest) -> HttpResponse:
    form = ExpenseFilterForm(request.GET or None)
    data = form.cleaned_data if form.is_valid() else {}
    queryset = visible_expenses(request.user).select_related(
        "applicant", "department", "project", "project_type"
    )
    queryset = apply_filters(queryset, data)
    fmt = request.GET.get("format", "xlsx")
    count = queryset.count()
    if count > 10000:
        messages.error(request, "匯出筆數超過 10,000 筆，請縮小日期或條件範圍。")
        return redirect("expenses:list")
    log_export(request.user, kind=fmt, count=count, filters=request.GET.dict())
    if fmt == "csv":
        return build_csv_response(queryset)
    return build_xlsx_response(queryset)


@login_required
def report_view(request: HttpRequest) -> HttpResponse:
    today = timezone.localdate()
    try:
        year = int(request.GET.get("year") or today.year)
    except ValueError:
        year = today.year
    year = max(2000, min(year, today.year + 1))
    quarter_raw = request.GET.get("quarter") or ""
    month_raw = request.GET.get("month") or ""
    quarter = int(quarter_raw) if quarter_raw.isdigit() and 1 <= int(quarter_raw) <= 4 else None
    month = int(month_raw) if month_raw.isdigit() and 1 <= int(month_raw) <= 12 else None
    data = report_data(request.user, year=year, quarter=quarter, month=month)
    charts_json = json.dumps(
        {
            "monthly": data["monthly"],
            "department_share": {
                "labels": [row["department__name"] or "未指定" for row in data["by_department"]],
                "values": [float(row["total"]) for row in data["by_department"]],
            },
            "category_share": {
                "labels": [row["category__name"] for row in data["by_category"]],
                "values": [float(row["total"]) for row in data["by_category"]],
            },
        },
        ensure_ascii=False,
    )
    return render(
        request,
        "reports/index.html",
        {
            "data": data,
            "charts_json": charts_json,
            "year": year,
            "quarter": quarter,
            "month": month,
            "years": list(range(today.year - 3, today.year + 1)),
        },
    )
