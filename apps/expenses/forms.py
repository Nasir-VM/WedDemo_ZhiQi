from __future__ import annotations

from django import forms
from django.forms import inlineformset_factory

from apps.core.forms import style_form
from apps.expenses.models import Expense, ExpenseCategory, Invoice, LineItem
from apps.expenses.uploads import inspect_upload


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["department", "project_type", "project", "apply_date", "reason"]
        widgets = {
            "apply_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(attrs={"rows": 3, "placeholder": "請說明費用用途與事由"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user is not None and not user.can_manage_org:
            self.fields["department"].queryset = self.fields["department"].queryset.filter(
                pk=user.department_id
            )
            self.fields["project"].queryset = self.fields["project"].queryset.filter(
                department_id=user.department_id
            )
        self.fields["project"].queryset = self.fields["project"].queryset.filter(
            status__in=["planning", "active"]
        )
        self.fields["project_type"].queryset = self.fields["project_type"].queryset.filter(
            is_active=True
        )
        style_form(self)

    def clean(self):
        cleaned = super().clean()
        project = cleaned.get("project")
        project_type = cleaned.get("project_type")
        if project is not None:
            if project.status == "closed":
                self.add_error("project", "此計畫已結案，無法再新增核銷。")
            if project_type is not None and project.project_type_id != project_type.pk:
                self.add_error("project_type", "計畫類型與所選計畫不一致。")
            elif project_type is None:
                cleaned["project_type"] = project.project_type
        if self.user is not None and not cleaned.get("department") and self.user.department_id:
            cleaned["department"] = self.user.department
        if not cleaned.get("department"):
            self.add_error("department", "請選擇部門（或請管理員為您設定部門）。")
        return cleaned


class InvoiceForm(forms.ModelForm):
    attachment = forms.FileField(
        label="發票影像／PDF",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "accept": "image/jpeg,image/png,application/pdf",
                "capture": "environment",
            }
        ),
    )

    class Meta:
        model = Invoice
        fields = [
            "invoice_type",
            "invoice_no",
            "issue_date",
            "seller_name",
            "seller_tax_id",
            "buyer_tax_id",
            "tax_rate",
            "note",
        ]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "invoice_no": forms.TextInput(
                attrs={"placeholder": "AB12345678", "maxlength": 10, "autocapitalize": "characters"}
            ),
            "seller_tax_id": forms.TextInput(attrs={"placeholder": "8 位數字", "maxlength": 8}),
            "buyer_tax_id": forms.TextInput(attrs={"placeholder": "8 位數字", "maxlength": 8}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)
        self.upload_info = None

    def clean_attachment(self):
        upload = self.cleaned_data.get("attachment")
        if upload:
            self.upload_info = inspect_upload(upload)
        return upload

    def clean(self):
        cleaned = super().clean()
        number = (cleaned.get("invoice_no") or "").strip().upper()
        seller = (cleaned.get("seller_tax_id") or "").strip()
        cleaned["invoice_no"] = number
        cleaned["seller_tax_id"] = seller
        if number and seller:
            duplicates = Invoice.objects.filter(invoice_no=number, seller_tax_id=seller)
            if self.instance.pk:
                duplicates = duplicates.exclude(pk=self.instance.pk)
            if duplicates.exists():
                raise forms.ValidationError(
                    "重複發票：此「發票號碼 + 賣方統編」已核銷過，請勿重複申報。"
                )
        return cleaned


class LineItemForm(forms.ModelForm):
    class Meta:
        model = LineItem
        fields = ["name", "spec", "quantity", "unit_price", "category", "note"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"step": "0.01", "min": "0.01"}),
            "unit_price": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = ExpenseCategory.objects.filter(is_active=True)
        style_form(self)

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity is None or quantity <= 0:
            raise forms.ValidationError("數量必須大於 0。")
        return quantity

    def clean_unit_price(self):
        price = self.cleaned_data.get("unit_price")
        if price is None or price < 0:
            raise forms.ValidationError("單價不可為負數。")
        return price


LineItemFormSet = inlineformset_factory(
    Invoice,
    LineItem,
    form=LineItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class ExpenseFilterForm(forms.Form):
    SORT_CHOICES = [
        ("-apply_date", "申請日期（新→舊）"),
        ("apply_date", "申請日期（舊→新）"),
        ("-total_amount", "金額（高→低）"),
        ("total_amount", "金額（低→高）"),
        ("number", "單號"),
        ("status", "狀態"),
    ]
    PAGE_SIZES = [("20", "20 筆"), ("50", "50 筆"), ("100", "100 筆")]

    q = forms.CharField(label="關鍵字", required=False)
    date_from = forms.DateField(
        label="起始日", required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    date_to = forms.DateField(
        label="結束日", required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    department = forms.ModelChoiceField(
        label="部門", required=False, queryset=None, empty_label="全部部門"
    )
    project = forms.ModelChoiceField(
        label="計畫", required=False, queryset=None, empty_label="全部計畫"
    )
    project_type = forms.ModelChoiceField(
        label="計畫類型", required=False, queryset=None, empty_label="全部類型"
    )
    category = forms.ModelChoiceField(
        label="費用科目", required=False, queryset=None, empty_label="全部科目"
    )
    vendor = forms.CharField(label="廠商", required=False)
    status = forms.ChoiceField(
        label="狀態", required=False, choices=[("", "全部狀態")] + list(Expense.Status.choices)
    )
    amount_min = forms.DecimalField(label="金額下限", required=False, min_value=0)
    amount_max = forms.DecimalField(label="金額上限", required=False, min_value=0)
    invoice_no = forms.CharField(label="發票號碼", required=False)
    applicant = forms.ModelChoiceField(
        label="申請人", required=False, queryset=None, empty_label="全部申請人"
    )
    sort = forms.ChoiceField(label="排序", required=False, choices=SORT_CHOICES)
    page_size = forms.ChoiceField(label="每頁筆數", required=False, choices=PAGE_SIZES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.accounts.models import Department, User
        from apps.expenses.models import ExpenseCategory
        from apps.projects.models import Project, ProjectType

        self.fields["department"].queryset = Department.objects.filter(is_active=True)
        self.fields["project"].queryset = Project.objects.all()
        self.fields["project_type"].queryset = ProjectType.objects.filter(is_active=True)
        self.fields["category"].queryset = ExpenseCategory.objects.filter(is_active=True)
        self.fields["applicant"].queryset = User.objects.filter(is_active=True).order_by("username")
        style_form(self)


class AttachmentForm(forms.Form):
    file = forms.FileField(
        label="附件",
        widget=forms.ClearableFileInput(
            attrs={
                "accept": "image/jpeg,image/png,application/pdf",
                "capture": "environment",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)
