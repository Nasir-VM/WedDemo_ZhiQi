from __future__ import annotations

from decimal import Decimal

from django.core.cache import cache
from django.db import models


class SystemSetting(models.Model):

    company_name = models.CharField("公司名稱", max_length=100, default="志氣企業")
    announcement = models.TextField("公司公告", blank=True)
    announcement_updated_at = models.DateTimeField("公告更新時間", null=True, blank=True)
    approval_threshold = models.DecimalField(
        "加簽金額門檻", max_digits=14, decimal_places=2, default=Decimal("50000.00")
    )
    default_tax_rate = models.DecimalField(
        "預設稅率(%)", max_digits=5, decimal_places=2, default=Decimal("5.00")
    )
    dashboard_cache_seconds = models.PositiveSmallIntegerField("Dashboard 快取秒數", default=60)
    backup_retention = models.PositiveSmallIntegerField("備份保留份數", default=14)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "系統設定"
        verbose_name_plural = "系統設定"

    def __str__(self) -> str:
        return f"系統設定（{self.company_name}）"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete("system_setting")

    @classmethod
    def load(cls) -> SystemSetting:
        cached = cache.get("system_setting")
        if cached is not None:
            return cached
        obj, _ = cls.objects.get_or_create(pk=1)
        cache.set("system_setting", obj, 300)
        return obj
