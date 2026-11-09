from __future__ import annotations

from django import forms

from apps.core.forms import StyledModelForm, style_form
from apps.projects.models import Project


class ProjectForm(StyledModelForm):
    class Meta:
        model = Project
        fields = [
            "code",
            "name",
            "project_type",
            "owner",
            "department",
            "start_date",
            "end_date",
            "budget_total",
            "status",
            "budget_control",
            "description",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["owner"].queryset = self.fields["owner"].queryset.filter(is_active=True)
        self.fields["project_type"].queryset = self.fields["project_type"].queryset.filter(
            is_active=True
        )
        style_form(self)
