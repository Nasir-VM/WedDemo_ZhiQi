from __future__ import annotations

import contextlib
import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q, Sum
from django.utils import timezone

from apps.core.tax import validate_tax_id
from apps.core.utils import quantize_money

INVOICE_NO_PATTERN = r"^[A-Z]{2}\d{8}$"


def invoice_upload_path(instance: InvoiceAttachment, filename: str) -> str:

    ext_map = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "application/pdf": "pdf",
    }
    ext = ext_map.get(getattr(instance, "content_type", ""), "bin")
    stamp = timezone.localdate().strftime("%Y/%m")
    return f"invoices/{stamp}/{uuid.uuid4().hex}.{ext}"


class Vendor(models.Model):
    name = models.CharField("廠商名稱", max_length=150)
    tax_id = models.CharField("統一編號", max_length=8, unique=True, null=True, blank=True)
    contact_person = models.CharField("聯絡人", max_length=80, blank=True)
    phone = models.CharField("電話", max_length=40, blank=True)
    email = models.EmailField("Email", blank=True)
    address = models.CharField("地址", max_length=200, blank=True)
    is_active = models.BooleanField("啟用", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "廠商"
        verbose_name_plural = "廠商"
        ordering = ["name"]
        indexes = [models.Index(fields=["name"], name="vendor_name_idx")]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if self.tax_id:
            validate_tax_id(self.tax_id)


class ExpenseCategory(models.Model):
    code = models.CharField("代碼", max_length=20, unique=True)
    name = models.CharField("名稱", max_length=80)
    description = models.TextField("說明", blank=True)
    is_active = models.BooleanField("啟用", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "費用科目"
        verbose_name_plural = "費用科目"
        ordering = ["code"]

    def __str__(self) -> str:
        return self.name


class Expense(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        SUBMITTED = "submitted", "已送審"
        MANAGER_REVIEW = "manager_review", "主管審核中"
        EXEC_REVIEW = "exec_review", "上層加簽"
        FINANCE_REVIEW = "finance_review", "財務審核中"
        APPROVED = "approved", "已核准"
        PAID = "paid", "已撥款"
        RETURNED = "returned", "退回修改"
        REJECTED = "rejected", "駁回"

    number = models.CharField("單號", max_length=30, unique=True, blank=True)
    applicant = models.ForeignKey(
        "accounts.User",
        verbose_name="申請人",
        on_delete=models.PROTECT,
        related_name="expenses",
    )
    department = models.ForeignKey(
        "accounts.Department",
        verbose_name="部門",
        on_delete=models.PROTECT,
        related_name="expenses",
    )
    project_type = models.ForeignKey(
        "projects.ProjectType",
        verbose_name="計畫類型",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="expenses",
    )
    project = models.ForeignKey(
        "projects.Project",
        verbose_name="計畫",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="expenses",
    )
    apply_date = models.DateField("申請日期", default=timezone.localdate)
    reason = models.TextField("事由")
    total_amount = models.DecimalField(
        "總金額", max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    status = models.CharField("狀態", max_length=20, choices=Status.choices, default=Status.DRAFT)
    version = models.PositiveIntegerField("版本", default=0)
    submitted_at = models.DateTimeField("送審時間", null=True, blank=True)
    approved_at = models.DateTimeField("核准時間", null=True, blank=True)
    paid_at = models.DateTimeField("撥款時間", null=True, blank=True)
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)

    class Meta:
        verbose_name = "核銷單"
        verbose_name_plural = "核銷單"
        ordering = ["-apply_date", "-id"]
        indexes = [
            models.Index(fields=["status", "apply_date"], name="expense_status_date_idx"),
            models.Index(fields=["department", "status"], name="expense_dept_status_idx"),
            models.Index(fields=["applicant", "status"], name="expense_applicant_idx"),
            models.Index(fields=["project", "status"], name="expense_project_idx"),
            models.Index(fields=["apply_date"], name="expense_date_idx"),
        ]

    def __str__(self) -> str:
        return self.number or f"核銷單 #{self.pk}"

    @property
    def is_editable(self) -> bool:
        return self.status in {self.Status.DRAFT, self.Status.RETURNED}

    @property
    def is_locked(self) -> bool:
        return self.status in {self.Status.APPROVED, self.Status.PAID}

    @property
    def status_label(self) -> str:
        return self.get_status_display()

    def can_edit(self, user) -> bool:
        if not user.is_authenticated or user.is_readonly or not self.is_editable:
            return False
        if user.is_admin_role:
            return True
        return self.applicant_id == user.id

    def save(self, *args, **kwargs):
        if not self.number:
            from apps.expenses.numbering import next_expense_number

            self.number = next_expense_number()
        super().save(*args, **kwargs)

    def recalc_total(self, *, save: bool = True) -> Decimal:
        total = self.invoices.aggregate(value=Sum("total_amount"))["value"] or Decimal("0.00")
        total = quantize_money(total)
        if save and self.pk and total != self.total_amount:
            Expense.objects.filter(pk=self.pk).update(
                total_amount=total, version=F("version") + 1, updated_at=timezone.now()
            )
            self.total_amount = total
            self.refresh_from_db(fields=["version", "updated_at", "total_amount"])
        else:
            self.total_amount = total
        return total


class Invoice(models.Model):
    class InvoiceType(models.TextChoices):
        ELECTRONIC = "electronic", "電子發票"
        TRIPLICATE = "triplicate", "三聯式"
        DUPLICATE = "duplicate", "二聯式"
        RECEIPT = "receipt", "收據"
        OTHER = "other", "其他"

    expense = models.ForeignKey(
        Expense, verbose_name="核銷單", on_delete=models.CASCADE, related_name="invoices"
    )
    invoice_type = models.CharField(
        "發票類型", max_length=20, choices=InvoiceType.choices, default=InvoiceType.ELECTRONIC
    )
    invoice_no = models.CharField("發票號碼", max_length=10, blank=True)
    issue_date = models.DateField("開立日期")
    seller_name = models.CharField("賣方名稱", max_length=150)
    seller_tax_id = models.CharField("賣方統編", max_length=8, blank=True)
    buyer_tax_id = models.CharField("買方統編", max_length=8, blank=True)
    untaxed_amount = models.DecimalField(
        "未稅金額", max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    tax_rate = models.DecimalField(
        "稅率(%)", max_digits=5, decimal_places=2, default=Decimal("5.00")
    )
    tax_amount = models.DecimalField(
        "稅額", max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    total_amount = models.DecimalField(
        "含稅總額", max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    note = models.CharField("備註", max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "發票"
        verbose_name_plural = "發票"
        ordering = ["issue_date", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["invoice_no", "seller_tax_id"],
                condition=~Q(invoice_no=""),
                name="uniq_invoice_no_seller_tax",
            )
        ]
        indexes = [
            models.Index(fields=["invoice_no"], name="invoice_no_idx"),
            models.Index(fields=["seller_tax_id"], name="invoice_seller_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.get_invoice_type_display()} {self.invoice_no or '(無號)'}"

    @property
    def requires_invoice_number(self) -> bool:
        return self.invoice_type in {
            self.InvoiceType.ELECTRONIC,
            self.InvoiceType.TRIPLICATE,
            self.InvoiceType.DUPLICATE,
        }

    def clean(self) -> None:
        import re

        errors: dict[str, str] = {}
        number = (self.invoice_no or "").strip().upper()
        if self.requires_invoice_number and not number:
            errors["invoice_no"] = "此發票類型必須填寫發票號碼。"
        if number and not re.fullmatch(INVOICE_NO_PATTERN, number):
            errors["invoice_no"] = "發票號碼須為 2 個大寫英文字母 + 8 位數字（例：AB12345678）。"
        if self.requires_invoice_number and not (self.seller_tax_id or "").strip():
            errors["seller_tax_id"] = "此發票類型必須填寫賣方統一編號。"
        for field in ("seller_tax_id", "buyer_tax_id"):
            value = (getattr(self, field) or "").strip()
            if value:
                try:
                    validate_tax_id(value)
                except ValidationError as exc:
                    errors[field] = exc.messages[0]
        if self.tax_rate is not None and not (Decimal("0") <= self.tax_rate <= Decimal("100")):
            errors["tax_rate"] = "稅率必須介於 0 到 100 之間。"
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.invoice_no = (self.invoice_no or "").strip().upper()
        self.seller_tax_id = (self.seller_tax_id or "").strip()
        self.buyer_tax_id = (self.buyer_tax_id or "").strip()
        super().save(*args, **kwargs)

    def recalc_totals(self, *, save: bool = True) -> Decimal:
        untaxed = self.items.aggregate(value=Sum("subtotal"))["value"] or Decimal("0.00")
        untaxed = quantize_money(untaxed)
        tax = quantize_money(untaxed * (self.tax_rate or Decimal("0")) / Decimal("100"))
        total = quantize_money(untaxed + tax)
        self.untaxed_amount = untaxed
        self.tax_amount = tax
        self.total_amount = total
        if save and self.pk:
            Invoice.objects.filter(pk=self.pk).update(
                untaxed_amount=untaxed,
                tax_amount=tax,
                total_amount=total,
                updated_at=timezone.now(),
            )
        return total


class LineItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, verbose_name="發票", on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField("品名", max_length=150)
    spec = models.CharField("規格", max_length=150, blank=True)
    quantity = models.DecimalField("數量", max_digits=10, decimal_places=2, default=Decimal("1"))
    unit_price = models.DecimalField("單價", max_digits=12, decimal_places=2, default=Decimal("0"))
    subtotal = models.DecimalField(
        "小計", max_digits=14, decimal_places=2, default=Decimal("0"), editable=False
    )
    category = models.ForeignKey(
        ExpenseCategory,
        verbose_name="費用科目",
        on_delete=models.PROTECT,
        related_name="line_items",
    )
    note = models.CharField("備註", max_length=200, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        verbose_name = "品項"
        verbose_name_plural = "品項"
        ordering = ["sort_order", "id"]
        indexes = [models.Index(fields=["category"], name="lineitem_category_idx")]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.subtotal = quantize_money((self.quantity or 0) * (self.unit_price or 0))
        super().save(*args, **kwargs)


class InvoiceAttachment(models.Model):
    invoice = models.ForeignKey(
        Invoice, verbose_name="發票", on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField("檔案", upload_to=invoice_upload_path)
    original_name = models.CharField("原始檔名", max_length=255)
    content_type = models.CharField("MIME", max_length=50)
    size = models.PositiveIntegerField("大小", default=0)
    sha256 = models.CharField("SHA256", max_length=64, blank=True)
    uploaded_by = models.ForeignKey(
        "accounts.User",
        verbose_name="上傳者",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attachments",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "發票附件"
        verbose_name_plural = "發票附件"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.original_name

    def delete(self, *args, **kwargs):
        storage = self.file.storage
        name = self.file.name
        result = super().delete(*args, **kwargs)
        if name:
            with contextlib.suppress(Exception):
                storage.delete(name)
        return result


class ApprovalLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "create", "建立"
        UPDATE = "update", "修改"
        SUBMIT = "submit", "送審"
        CLAIM = "claim", "接手審核"
        MANAGER_APPROVE = "manager_approve", "主管核准"
        EXEC_APPROVE = "exec_approve", "上層加簽核准"
        FINANCE_APPROVE = "finance_approve", "財務核准"
        PAY = "pay", "撥款"
        RETURN = "return", "退回修改"
        REJECT = "reject", "駁回"

    expense = models.ForeignKey(
        Expense, verbose_name="核銷單", on_delete=models.CASCADE, related_name="logs"
    )
    actor = models.ForeignKey(
        "accounts.User",
        verbose_name="操作人",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approval_logs",
    )
    action = models.CharField("動作", max_length=30, choices=Action.choices)
    from_status = models.CharField("原狀態", max_length=20, blank=True)
    to_status = models.CharField("新狀態", max_length=20, blank=True)
    comment = models.TextField("意見", blank=True)
    ip = models.GenericIPAddressField("IP", null=True, blank=True)
    created_at = models.DateTimeField("時間", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "簽核紀錄"
        verbose_name_plural = "簽核紀錄"
        ordering = ["created_at", "id"]

    def __str__(self) -> str:
        return f"{self.get_action_display()} {self.from_status}→{self.to_status}"


class DocumentSequence(models.Model):
    scope = models.CharField("用途", max_length=30)
    period = models.CharField("期間", max_length=10)
    last_value = models.PositiveIntegerField("最後序號", default=0)

    class Meta:
        verbose_name = "單號流水號"
        verbose_name_plural = "單號流水號"
        constraints = [
            models.UniqueConstraint(fields=["scope", "period"], name="uniq_sequence_scope_period")
        ]

    def __str__(self) -> str:
        return f"{self.scope}-{self.period}: {self.last_value}"
