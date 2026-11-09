from __future__ import annotations

from django.apps import apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate, dispatch_uid="core.create_system_setting")
def create_system_setting(sender, **kwargs) -> None:
    if getattr(sender, "name", "") != "apps.core":
        return
    SystemSetting = apps.get_model("core", "SystemSetting")
    SystemSetting.objects.get_or_create(pk=1)
