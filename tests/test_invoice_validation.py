from __future__ import annotations

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.expenses.forms import InvoiceForm
from apps.expenses.models import Invoice

pytestmark = pytest.mark.django_db


def test_invoice_requires_number_for_electronic():
    invoice = Invoice(
        invoice_type=Invoice.InvoiceType.ELECTRONIC,
        invoice_no="",
        issue_date="2026-01-01",
        seller_name="廠商",
        seller_tax_id="04595257",
        tax_rate=Decimal("5"),
    )
    with pytest.raises(ValidationError) as exc:
        invoice.clean()
    assert "invoice_no" in exc.value.message_dict


def test_invoice_rejects_bad_number():
    invoice = Invoice(
        invoice_type=Invoice.InvoiceType.ELECTRONIC,
        invoice_no="AB123",
        issue_date="2026-01-01",
        seller_name="廠商",
        seller_tax_id="04595257",
        tax_rate=Decimal("5"),
    )
    with pytest.raises(ValidationError):
        invoice.clean()


def test_invoice_form_rejects_duplicate_number(expense_factory, employee, department):
    expense = expense_factory(employee, department, invoice_no="AB12345678")
    form = InvoiceForm(
        data={
            "invoice_type": Invoice.InvoiceType.ELECTRONIC,
            "invoice_no": "AB12345678",
            "issue_date": "2026-02-01",
            "seller_name": "另一廠商",
            "seller_tax_id": "04595257",
            "buyer_tax_id": "",
            "tax_rate": "5",
            "note": "",
        },
        instance=Invoice(expense=expense),
    )
    assert not form.is_valid()
    assert "重複發票" in str(form.errors)


def test_invoice_form_rejects_invalid_tax_id(expense_factory, employee, department):
    expense = expense_factory(employee, department)
    form = InvoiceForm(
        data={
            "invoice_type": Invoice.InvoiceType.RECEIPT,
            "invoice_no": "",
            "issue_date": "2026-02-01",
            "seller_name": "小吃店",
            "seller_tax_id": "12345678",
            "buyer_tax_id": "",
            "tax_rate": "5",
            "note": "",
        },
        instance=Invoice(expense=expense),
    )
    assert not form.is_valid()
    assert "seller_tax_id" in form.errors


def test_invoice_totals_round_half_up(expense_factory, employee, department):
    expense = expense_factory(employee, department, amount=Decimal("100.05"))
    invoice = expense.invoices.get()
    invoice.tax_rate = Decimal("5")
    invoice.recalc_totals()
    invoice.refresh_from_db()
    assert invoice.untaxed_amount == Decimal("100.05")
    assert invoice.tax_amount == Decimal("5.00")
    assert invoice.total_amount == Decimal("105.05")
