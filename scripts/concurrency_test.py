#!/usr/bin/env python


from __future__ import annotations

import argparse
import os
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from decimal import Decimal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

os.environ.setdefault("DJANGO_DEBUG", "True")
os.environ.setdefault("DJANGO_SECRET_KEY", "dev-only-concurrency-test-key-do-not-use-in-production")

import django

django.setup()

from django.db import connections

from apps.accounts.models import Department, User
from apps.expenses.models import (
    ApprovalLog,
    Expense,
    ExpenseCategory,
    Invoice,
    LineItem,
)
from apps.expenses.services import create_expense, transition
from apps.projects.models import ProjectType


def _prepare_fixtures(threads: int) -> tuple[int, int, int, list[int]]:
    department, _ = Department.objects.get_or_create(code="CONC", defaults={"name": "併發測試部門"})
    project_type, _ = ProjectType.objects.get_or_create(
        code="GENERAL", defaults={"name": "一般營運"}
    )
    category, _ = ExpenseCategory.objects.get_or_create(code="MEALS", defaults={"name": "餐飲"})
    user_ids: list[int] = []
    for index in range(threads):
        user, created = User.objects.get_or_create(
            username=f"concurrency_{index}",
            defaults={
                "role": User.Role.EMPLOYEE,
                "department": department,
                "must_change_password": False,
            },
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
        elif user.department_id != department.pk or user.role != User.Role.EMPLOYEE:
            user.department = department
            user.role = User.Role.EMPLOYEE
            user.save(update_fields=["department", "role"])
        user_ids.append(user.pk)
    return department.pk, project_type.pk, category.pk, user_ids


def _create_one(
    *,
    user_id: int,
    department_id: int,
    project_type_id: int,
    category_id: int,
    invoice_no: str,
    marker: str,
    submit: bool,
) -> tuple[str, str]:
    try:
        user = User.objects.get(pk=user_id)
        expense = create_expense(
            applicant=user,
            data={
                "department_id": department_id,
                "project_type_id": project_type_id,
                "apply_date": date.today(),
                "reason": f"{marker} 併發測試",
            },
        )
        if submit:
            invoice = Invoice.objects.create(
                expense=expense,
                invoice_type=Invoice.InvoiceType.ELECTRONIC,
                invoice_no=invoice_no,
                issue_date=date.today(),
                seller_name="併發測試廠商",
                seller_tax_id="04595257",
                tax_rate=Decimal("0"),
            )
            LineItem.objects.create(
                invoice=invoice,
                name="併發測試品項",
                quantity=Decimal("1"),
                unit_price=Decimal("100"),
                category_id=category_id,
            )
            invoice.recalc_totals()
            expense.recalc_total()
            expense = transition(expense_id=expense.pk, action="submit", actor=user)
        return expense.number, expense.status
    finally:
        connections.close_all()


def _run(
    *,
    threads: int,
    per_thread: int,
    phase: str,
    keep: bool,
) -> int:
    marker = f"[conc-{uuid.uuid4().hex[:8]}]"
    department_id, project_type_id, category_id, user_ids = _prepare_fixtures(threads)
    submit = phase in {"submit", "both"}
    total = threads * per_thread
    results: list[tuple[str, str]] = []
    errors: list[str] = []
    lock = threading.Lock()
    generated_invoice_numbers: set[str] = set()

    def next_invoice_no() -> str:
        with lock:
            while True:
                candidate = f"AB{uuid.uuid4().int % 100_000_000:08d}"
                exists = Invoice.objects.filter(
                    invoice_no=candidate, seller_tax_id="04595257"
                ).exists()
                if candidate not in generated_invoice_numbers and not exists:
                    generated_invoice_numbers.add(candidate)
                    return candidate

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for thread_index in range(threads):
            for _item_index in range(per_thread):
                futures.append(
                    executor.submit(
                        _create_one,
                        user_id=user_ids[thread_index],
                        department_id=department_id,
                        project_type_id=project_type_id,
                        category_id=category_id,
                        invoice_no=next_invoice_no(),
                        marker=marker,
                        submit=submit,
                    )
                )
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as exc:
                errors.append(f"{type(exc).__name__}: {exc}")

    elapsed = time.perf_counter() - started
    numbers = [number for number, _ in results]
    statuses = [status for _, status in results]
    expenses = Expense.objects.filter(reason__startswith=marker)
    log_count = ApprovalLog.objects.filter(expense__reason__startswith=marker).count()
    expected_logs = total * (2 if submit else 1)
    expected_status = Expense.Status.SUBMITTED if submit else Expense.Status.DRAFT

    checks = {
        "threads": threads,
        "per_thread": per_thread,
        "phase": phase,
        "expected_rows": total,
        "created_rows": expenses.count(),
        "unique_numbers": len(set(numbers)),
        "submitted_rows": sum(1 for status in statuses if status == expected_status),
        "approval_logs": log_count,
        "expected_approval_logs": expected_logs,
        "elapsed_seconds": round(elapsed, 3),
        "errors": len(errors),
    }
    ok = (
        not errors
        and checks["created_rows"] == total
        and checks["unique_numbers"] == total
        and checks["submitted_rows"] == total
        and checks["approval_logs"] == expected_logs
    )

    print("=== 併發測試結果 ===")
    for key, value in checks.items():
        print(f"{key}: {value}")
    if errors:
        print("--- 錯誤 ---")
        for error in errors[:20]:
            print(error)
    print(f"結果：{'PASS' if ok else 'FAIL'}")

    if not keep:
        deleted, _ = expenses.delete()
        print(f"清理：已刪除 {deleted} 筆測試相關資料（--keep 可保留）")
    else:
        print(f"保留測試資料，reason 前綴：{marker}")

    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="志氣企業核銷系統 SQLite 併發壓力測試")
    parser.add_argument("--threads", type=int, default=8, help="執行緒數（預設 8）")
    parser.add_argument("--per-thread", type=int, default=5, help="每執行緒筆數（預設 5）")
    parser.add_argument(
        "--phase",
        choices=["create", "submit", "both"],
        default="both",
        help="create=只建立；submit/both=建立後送審（預設 both）",
    )
    parser.add_argument("--keep", action="store_true", help="保留測試資料")
    args = parser.parse_args()
    if args.threads < 1 or args.per_thread < 1:
        parser.error("--threads 與 --per-thread 必須大於 0")
    return _run(
        threads=args.threads,
        per_thread=args.per_thread,
        phase=args.phase,
        keep=args.keep,
    )


if __name__ == "__main__":
    raise SystemExit(main())
