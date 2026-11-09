from __future__ import annotations

import csv
from io import BytesIO

from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from apps.core.utils import csv_safe

HEADERS = ["單號", "申請日期", "申請人", "部門", "計畫", "狀態", "金額", "事由"]
ONLY_FIELDS = (
    "number",
    "apply_date",
    "reason",
    "total_amount",
    "status",
    "applicant__username",
    "applicant__first_name",
    "applicant__last_name",
    "department__name",
    "project__code",
    "project__name",
    "project_type__name",
)


def _iter_rows(queryset):

    for expense in queryset.only(*ONLY_FIELDS).iterator(chunk_size=500):
        applicant = expense.applicant.get_full_name() or expense.applicant.username
        yield [
            expense.number,
            expense.apply_date.isoformat(),
            applicant,
            expense.department.name if expense.department_id else "",
            f"{expense.project.code} {expense.project.name}" if expense.project_id else "",
            expense.get_status_display(),
            float(expense.total_amount),
            expense.reason,
        ]


def _filename(extension: str) -> str:
    return f"expenses_{timezone.localdate():%Y%m%d}.{extension}"


def build_csv_response(queryset) -> HttpResponse:
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{_filename("csv")}"'
    response.write("\ufeff")
    writer = csv.writer(response)
    writer.writerow(HEADERS)
    for row in _iter_rows(queryset):
        writer.writerow([csv_safe(value) for value in row])
    return response


def build_xlsx_response(queryset) -> HttpResponse:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "核銷單"
    sheet.append(HEADERS)
    header_fill = PatternFill("solid", fgColor="1E3A8A")
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
    for row in _iter_rows(queryset):
        sheet.append(row)
    for index, width in enumerate([20, 12, 14, 14, 30, 12, 14, 40], start=1):
        sheet.column_dimensions[get_column_letter(index)].width = width
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for row in sheet.iter_rows(min_row=2, min_col=7, max_col=7):
        for cell in row:
            cell.number_format = "#,##0.00"
    buffer = BytesIO()
    workbook.save(buffer)
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{_filename("xlsx")}"'
    return response
