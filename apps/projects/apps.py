from __future__ import annotations

from django.apps import AppConfig, apps
from django.db.models.signals import post_migrate

DEFAULT_PROJECT_TYPES = [
    ("GENERAL", "一般營運", "日常營運支出"),
    ("PROJECT", "專案計畫", "客戶或內部專案"),
    ("RD", "研發計畫", "研發與創新"),
    ("MARKETING", "行銷活動", "廣告與行銷活動"),
    ("TRAVEL", "出差差旅", "出差與差旅"),
    ("EQUIPMENT", "設備採購", "設備與資產採購"),
    ("TRAINING", "教育訓練", "內外部教育訓練"),
]


class ProjectsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.projects"
    verbose_name = "計畫"

    def ready(self) -> None:
        post_migrate.connect(_create_defaults, sender=self, dispatch_uid="projects.defaults")


def _create_defaults(sender, **kwargs) -> None:
    if getattr(sender, "name", "") != "apps.projects":
        return
    ProjectType = apps.get_model("projects", "ProjectType")
    for code, name, description in DEFAULT_PROJECT_TYPES:
        ProjectType.objects.get_or_create(
            code=code, defaults={"name": name, "description": description}
        )
