from __future__ import annotations

from django.contrib import admin

from apps.expenses.models import (
    ApprovalLog,
    DocumentSequence,
    Expense,
    ExpenseCategory,
    Invoice,
    InvoiceAttachment,
    LineItem,
    Vendor,
)


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "tax_id", "contact_person", "phone", "is_active")
    search_fields = ("name", "tax_id")


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    search_fields = ("code", "name")


class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 0
    fields = ("invoice_type", "invoice_no", "issue_date", "seller_name", "total_amount")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("number", "applicant", "department", "status", "total_amount", "apply_date")
    list_filter = ("status", "department", "project_type")
    search_fields = ("number", "reason", "applicant__username")
    readonly_fields = ("number", "total_amount", "version", "created_at", "updated_at")
    inlines = [InvoiceInline]
    date_hierarchy = "apply_date"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_no", "seller_name", "seller_tax_id", "issue_date", "total_amount")
    search_fields = ("invoice_no", "seller_name", "seller_tax_id")


@admin.register(LineItem)
class LineItemAdmin(admin.ModelAdmin):
    list_display = ("name", "invoice", "quantity", "unit_price", "subtotal", "category")
    list_filter = ("category",)


@admin.register(InvoiceAttachment)
class InvoiceAttachmentAdmin(admin.ModelAdmin):
    list_display = ("original_name", "content_type", "size", "created_at")
    readonly_fields = ("sha256", "size", "content_type")


@admin.register(ApprovalLog)
class ApprovalLogAdmin(admin.ModelAdmin):
    list_display = ("expense", "actor", "action", "from_status", "to_status", "created_at")
    list_filter = ("action", "created_at")
    readonly_fields = (
        "expense",
        "actor",
        "action",
        "from_status",
        "to_status",
        "comment",
        "ip",
        "created_at",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(DocumentSequence)
class DocumentSequenceAdmin(admin.ModelAdmin):
    list_display = ("scope", "period", "last_value")
    readonly_fields = ("scope", "period", "last_value")
