from __future__ import annotations

from django.db import models

from apps.accounts.models import User


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "create", "新增"
        UPDATE = "update", "修改"
        DELETE = "delete", "刪除"
        LOGIN = "login", "登入"
        LOGOUT = "logout", "登出"
        LOGIN_FAILED = "login_failed", "登入失敗"
        EXPORT = "export", "匯出"
        PERMISSION = "permission_change", "權限變更"
        BACKUP = "backup", "備份"
        RESTORE = "restore", "還原"

    user = models.ForeignKey(
        User,
        verbose_name="使用者",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    username = models.CharField("帳號快照", max_length=150, blank=True)
    action = models.CharField("動作", max_length=30, choices=Action.choices, db_index=True)
    model_label = models.CharField("物件類型", max_length=100, blank=True, db_index=True)
    object_id = models.CharField("物件 ID", max_length=64, blank=True)
    object_repr = models.CharField("物件摘要", max_length=255, blank=True)
    changes = models.JSONField("差異", default=dict, blank=True)
    ip = models.GenericIPAddressField("IP", null=True, blank=True)
    user_agent = models.CharField("User-Agent", max_length=255, blank=True)
    created_at = models.DateTimeField("時間", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "稽核日誌"
        verbose_name_plural = "稽核日誌"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["model_label", "object_id"], name="audit_model_object_idx"),
            models.Index(fields=["user", "created_at"], name="audit_user_time_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.username} {self.get_action_display()}"
