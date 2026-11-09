from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.urls import reverse


class Department(models.Model):
    code = models.CharField("代碼", max_length=20, unique=True)
    name = models.CharField("名稱", max_length=100)
    parent = models.ForeignKey(
        "self",
        verbose_name="上層部門",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    is_active = models.BooleanField("啟用", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "部門"
        verbose_name_plural = "部門"
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.name}（{self.code}）"


class CostCenter(models.Model):
    code = models.CharField("代碼", max_length=20, unique=True)
    name = models.CharField("名稱", max_length=100)
    department = models.ForeignKey(
        Department,
        verbose_name="所屬部門",
        on_delete=models.PROTECT,
        related_name="cost_centers",
    )
    is_active = models.BooleanField("啟用", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "成本中心"
        verbose_name_plural = "成本中心"
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.name}（{self.code}）"


class UserManager(DjangoUserManager):
    pass


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "系統管理員"
        FINANCE = "finance", "財務"
        MANAGER = "manager", "部門主管"
        EMPLOYEE = "employee", "一般員工"
        AUDITOR = "auditor", "唯讀（稽核）"

    role = models.CharField("角色", max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    department = models.ForeignKey(
        Department,
        verbose_name="部門",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )
    cost_center = models.ForeignKey(
        CostCenter,
        verbose_name="成本中心",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )
    job_title = models.CharField("職稱", max_length=100, blank=True)
    employee_no = models.CharField("員工編號", max_length=30, unique=True, null=True, blank=True)
    phone = models.CharField("聯絡電話", max_length=30, blank=True)
    must_change_password = models.BooleanField("首次登入須改密碼", default=False)
    totp_secret = models.CharField("TOTP 密鑰", max_length=64, blank=True)
    totp_enabled = models.BooleanField("啟用兩步驟驗證", default=False)
    last_password_change = models.DateTimeField("密碼最後變更", null=True, blank=True)

    objects = UserManager()

    class Meta:
        verbose_name = "使用者"
        verbose_name_plural = "使用者"
        indexes = [
            models.Index(fields=["role", "department"], name="user_role_dept_idx"),
        ]

    def __str__(self) -> str:
        return self.get_full_name() or self.username

    def save(self, *args, **kwargs):
        if self.role == self.Role.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    @property
    def is_admin_role(self) -> bool:
        return self.is_superuser or self.role == self.Role.ADMIN

    @property
    def can_manage_org(self) -> bool:
        return self.is_admin_role

    @property
    def can_manage_master(self) -> bool:
        return self.is_admin_role or self.role == self.Role.FINANCE

    @property
    def can_view_all(self) -> bool:
        return self.is_admin_role or self.role in {self.Role.FINANCE, self.Role.AUDITOR}

    @property
    def is_readonly(self) -> bool:
        return self.role == self.Role.AUDITOR and not self.is_superuser

    @property
    def can_approve_manager(self) -> bool:
        return self.is_admin_role or self.role == self.Role.MANAGER

    @property
    def can_approve_finance(self) -> bool:
        return self.is_admin_role or self.role == self.Role.FINANCE

    @property
    def can_approve_exec(self) -> bool:
        return self.is_admin_role

    @property
    def can_create_expense(self) -> bool:
        return not self.is_readonly

    def get_absolute_url(self) -> str:
        return reverse("accounts:profile")
