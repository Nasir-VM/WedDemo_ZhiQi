from __future__ import annotations

from django.apps import AppConfig, apps
from django.db.models.signals import post_migrate

DEFAULT_CATEGORIES = [
    ("TRAVEL", "差旅", "交通、住宿與出差相關"),
    ("TRANSPORT", "交通", "計程車、高鐵、油資等"),
    ("MEALS", "餐飲", "餐費與招待"),
    ("OFFICE", "辦公用品", "文具與日常用品"),
    ("EQUIPMENT", "設備", "設備與資產"),
    ("TRAINING", "教育訓練", "課程與研習"),
    ("MARKETING", "廣告行銷", "廣告、投放與活動"),
    ("ENTERTAINMENT", "交際費", "客戶交際"),
    ("OTHER", "其他", "其他費用"),
]


class ExpensesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.expenses"
    verbose_name = "核銷"

    def ready(self) -> None:
        post_migrate.connect(_create_categories, sender=self, dispatch_uid="expenses.defaults")


def _create_categories(sender, **kwargs) -> None:
    if getattr(sender, "name", "") != "apps.expenses":
        return
    ExpenseCategory = apps.get_model("expenses", "ExpenseCategory")
    for code, name, description in DEFAULT_CATEGORIES:
        ExpenseCategory.objects.get_or_create(
            code=code, defaults={"name": name, "description": description}
        )
