from __future__ import annotations

from django.db import models

from apps.accounts.models import User


class Notification(models.Model):
    class Level(models.TextChoices):
        INFO = "info", "資訊"
        SUCCESS = "success", "成功"
        WARNING = "warning", "提醒"
        DANGER = "danger", "警示"

    user = models.ForeignKey(
        User, verbose_name="收件人", on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField("標題", max_length=150)
    message = models.TextField("內容", blank=True)
    url = models.CharField("連結", max_length=300, blank=True)
    level = models.CharField("等級", max_length=20, choices=Level.choices, default=Level.INFO)
    is_read = models.BooleanField("已讀", default=False)
    created_at = models.DateTimeField("建立時間", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "站內通知"
        verbose_name_plural = "站內通知"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "created_at"], name="notif_user_read_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.title}"
