from __future__ import annotations

from django import forms

from apps.core.tax import validate_tax_id


def style_form(form: forms.BaseForm) -> None:

    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault("class", "checkbox")
        elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
            widget.attrs.setdefault("class", "select")
        elif isinstance(widget, forms.Textarea):
            widget.attrs.setdefault("class", "textarea")
            widget.attrs.setdefault("rows", 3)
        else:
            widget.attrs.setdefault("class", "input")
        if field.required:
            widget.attrs.setdefault("aria-required", "true")


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)


class DepartmentForm(StyledModelForm):
    class Meta:
        from apps.accounts.models import Department

        model = Department
        fields = ["code", "name", "parent", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["parent"].queryset = self.fields["parent"].queryset.exclude(
                pk=self.instance.pk
            )


class CostCenterForm(StyledModelForm):
    class Meta:
        from apps.accounts.models import CostCenter

        model = CostCenter
        fields = ["code", "name", "department", "is_active"]


class VendorForm(StyledModelForm):
    class Meta:
        from apps.expenses.models import Vendor

        model = Vendor
        fields = ["name", "tax_id", "contact_person", "phone", "email", "address", "is_active"]

    def clean_tax_id(self) -> str:
        value = (self.cleaned_data.get("tax_id") or "").strip()
        if value:
            validate_tax_id(value)
        return value


class ExpenseCategoryForm(StyledModelForm):
    class Meta:
        from apps.expenses.models import ExpenseCategory

        model = ExpenseCategory
        fields = ["code", "name", "description", "is_active"]


class ProjectTypeForm(StyledModelForm):
    class Meta:
        from apps.projects.models import ProjectType

        model = ProjectType
        fields = ["code", "name", "description", "is_active"]
