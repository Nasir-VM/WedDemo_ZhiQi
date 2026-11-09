from __future__ import annotations

from django.db import models


class ProjectType(models.Model):
    code = models.CharField("代碼", max_length=20, unique=True)
    name = models.CharField("名稱", max_length=80)
    description = models.TextField("說明", blank=True)
    is_active = models.BooleanField("啟用", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "計畫類型"
        verbose_name_plural = "計畫類型"
        ordering = ["code"]

    def __str__(self) -> str:
        return self.name


class Project(models.Model):
    class Status(models.TextChoices):
        PLANNING = "planning", "規劃中"
        ACTIVE = "active", "進行中"
        CLOSED = "closed", "結案"

    class BudgetControl(models.TextChoices):
        WARN = "warn", "警告"
        BLOCK = "block", "阻擋"

    code = models.CharField("計畫代碼", max_length=30, unique=True)
    name = models.CharField("計畫名稱", max_length=150)
    project_type = models.ForeignKey(
        ProjectType, verbose_name="計畫類型", on_delete=models.PROTECT, related_name="projects"
    )
    owner = models.ForeignKey(
        "accounts.User",
        verbose_name="負責人",
        on_delete=models.PROTECT,
        related_name="owned_projects",
    )
    department = models.ForeignKey(
        "accounts.Department",
        verbose_name="部門",
        on_delete=models.PROTECT,
        related_name="projects",
    )
    start_date = models.DateField("開始日期")
    end_date = models.DateField("結束日期")
    budget_total = models.DecimalField("預算總額", max_digits=14, decimal_places=2, default=0)
    spent_amount = models.DecimalField("已核銷金額", max_digits=14, decimal_places=2, default=0)
    status = models.CharField("狀態", max_length=20, choices=Status.choices, default=Status.ACTIVE)
    budget_control = models.CharField(
        "預算控管", max_length=10, choices=BudgetControl.choices, default=BudgetControl.WARN
    )
    description = models.TextField("說明", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "計畫"
        verbose_name_plural = "計畫"
        ordering = ["code"]
        indexes = [
            models.Index(fields=["status", "department"], name="project_status_dept_idx"),
            models.Index(fields=["project_type"], name="project_type_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.code} {self.name}"

    @property
    def remaining_budget(self):
        return self.budget_total - self.spent_amount

    @property
    def execution_rate(self) -> float:
        if not self.budget_total:
            return 0.0
        return float(self.spent_amount / self.budget_total * 100)

    @property
    def is_over_budget(self) -> bool:
        return self.spent_amount > self.budget_total

    @property
    def is_near_budget(self) -> bool:
        return self.execution_rate >= 90

    def clean(self) -> None:
        from django.core.exceptions import ValidationError

        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "結束日期不可早於開始日期。"})
        if self.budget_total is not None and self.budget_total < 0:
            raise ValidationError({"budget_total": "預算不可為負數。"})
