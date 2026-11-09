from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.accounts.models import CostCenter, Department, User
from apps.core.models import SystemSetting
from apps.expenses.models import (
    ApprovalLog,
    Expense,
    ExpenseCategory,
    Invoice,
    LineItem,
    Vendor,
)
from apps.projects.models import Project, ProjectType

DEMO_PASSWORD = "Demo1234!x"
TAX_IDS = ["04595257", "10458575", "22099131", "53114571"]


class Command(BaseCommand):
    help = "建立可重複執行的示範資料（部門、使用者、計畫、費用科目與核銷單）。"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--password", default=DEMO_PASSWORD, help="示範帳號密碼。")

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        password = options["password"]
        today = timezone.localdate()

        departments = {}
        for code, name in (("HQ", "總管理處"), ("RD", "研發部"), ("SALES", "業務部")):
            department, _ = Department.objects.get_or_create(code=code, defaults={"name": name})
            departments[code] = department
        for code, name, dept in (
            ("CC-HQ", "總管理處成本中心", "HQ"),
            ("CC-RD", "研發成本中心", "RD"),
            ("CC-SALES", "業務成本中心", "SALES"),
        ):
            CostCenter.objects.get_or_create(
                code=code, defaults={"name": name, "department": departments[dept]}
            )

        users = {
            "admin": ("系統管理員", User.Role.ADMIN, "HQ"),
            "manager": ("研發主管", User.Role.MANAGER, "RD"),
            "finance": ("財務專員", User.Role.FINANCE, "HQ"),
            "employee": ("研發工程師", User.Role.EMPLOYEE, "RD"),
            "auditor": ("稽核人員", User.Role.AUDITOR, "HQ"),
        }
        created_users: dict[str, User] = {}
        for username, (full_name, role, dept_code) in users.items():
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": full_name,
                    "role": role,
                    "department": departments[dept_code],
                    "email": f"{username}@example.com",
                    "employee_no": f"E{username.upper()[:4]}",
                },
            )
            user.role = role
            user.department = departments[dept_code]
            user.is_active = True
            user.must_change_password = False
            if created or not user.has_usable_password():
                user.set_password(password)
            if role == User.Role.ADMIN:
                user.is_staff = True
                user.is_superuser = True
            user.save()
            created_users[username] = user

        project_type, _ = ProjectType.objects.get_or_create(
            code="GENERAL", defaults={"name": "一般營運", "description": "日常營運支出"}
        )
        rd_type, _ = ProjectType.objects.get_or_create(
            code="RD", defaults={"name": "研發計畫", "description": "研發與創新"}
        )
        projects = {}
        for code, name, ptype, dept, owner, budget in (
            (
                "PRJ-2026-001",
                "AI 產品研發",
                rd_type,
                departments["RD"],
                created_users["manager"],
                Decimal("1200000"),
            ),
            (
                "PRJ-2026-002",
                "年度品牌行銷",
                project_type,
                departments["SALES"],
                created_users["manager"],
                Decimal("600000"),
            ),
        ):
            project, _ = Project.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "project_type": ptype,
                    "department": dept,
                    "owner": owner,
                    "start_date": today.replace(month=1, day=1),
                    "end_date": today.replace(month=12, day=31),
                    "budget_total": budget,
                    "budget_control": Project.BudgetControl.WARN,
                    "description": "示範計畫資料",
                },
            )
            projects[code] = project

        categories = {}
        for code, name in (
            ("TRAVEL", "差旅"),
            ("TRANSPORT", "交通"),
            ("MEALS", "餐飲"),
            ("OFFICE", "辦公用品"),
            ("EQUIPMENT", "設備"),
            ("TRAINING", "教育訓練"),
            ("MARKETING", "廣告行銷"),
            ("OTHER", "其他"),
        ):
            category, _ = ExpenseCategory.objects.get_or_create(code=code, defaults={"name": name})
            categories[code] = category

        vendors = []
        for index, (name, tax_id) in enumerate(
            (
                ("志氣科技股份有限公司", TAX_IDS[0]),
                ("台灣雲端服務股份有限公司", TAX_IDS[1]),
                ("城市商旅股份有限公司", TAX_IDS[2]),
                ("安心辦公用品有限公司", TAX_IDS[3]),
            )
        ):
            vendor, _ = Vendor.objects.get_or_create(
                tax_id=tax_id,
                defaults={"name": name, "contact_person": f"聯絡人{index + 1}"},
            )
            vendors.append(vendor)

        setting = SystemSetting.load()
        setting.company_name = "志氣企業"
        setting.announcement = "歡迎使用核銷系統。示範資料已建立，請以 admin / Demo1234!x 登入。"
        setting.announcement_updated_at = timezone.now()
        setting.approval_threshold = Decimal("50000.00")
        setting.save()

        if Expense.objects.exists():
            self.stdout.write(
                self.style.WARNING("已存在核銷單，略過示範單據建立（基礎資料已確保）。")
            )
            self._report()
            return

        demo_rows = [
            (
                "employee",
                "PRJ-2026-001",
                "MEALS",
                "客戶拜訪餐費",
                "2026-01-12",
                Expense.Status.PAID,
            ),
            (
                "employee",
                "PRJ-2026-001",
                "TRANSPORT",
                "高鐵出差交通",
                "2026-02-08",
                Expense.Status.APPROVED,
            ),
            (
                "employee",
                "PRJ-2026-001",
                "EQUIPMENT",
                "開發用螢幕",
                "2026-03-19",
                Expense.Status.FINANCE_REVIEW,
            ),
            (
                "employee",
                "PRJ-2026-002",
                "MARKETING",
                "社群廣告投放",
                "2026-04-05",
                Expense.Status.EXEC_REVIEW,
            ),
            (
                "manager",
                "PRJ-2026-002",
                "TRAVEL",
                "南部客戶出差住宿",
                "2026-05-16",
                Expense.Status.MANAGER_REVIEW,
            ),
            (
                "manager",
                "PRJ-2026-001",
                "TRAINING",
                "AI 技術研討會",
                "2026-06-22",
                Expense.Status.SUBMITTED,
            ),
            (
                "employee",
                "PRJ-2026-001",
                "OFFICE",
                "實驗室文具用品",
                "2026-07-03",
                Expense.Status.DRAFT,
            ),
            (
                "employee",
                "PRJ-2026-002",
                "OTHER",
                "臨時雜項支出",
                "2026-08-14",
                Expense.Status.RETURNED,
            ),
            (
                "employee",
                "PRJ-2026-001",
                "MEALS",
                "團隊會議餐盒",
                "2026-09-09",
                Expense.Status.REJECTED,
            ),
            (
                "manager",
                "PRJ-2026-001",
                "EQUIPMENT",
                "測試設備採購",
                "2026-10-21",
                Expense.Status.PAID,
            ),
        ]
        seq = 1
        for username, project_code, category_code, reason, apply_date, status in demo_rows:
            applicant = created_users[username]
            project = projects[project_code]
            expense = Expense.objects.create(
                applicant=applicant,
                department=applicant.department,
                project_type=project.project_type,
                project=project,
                apply_date=apply_date,
                reason=reason,
                status=status,
                submitted_at=timezone.now() if status != Expense.Status.DRAFT else None,
            )
            vendor = vendors[seq % len(vendors)]
            invoice = Invoice.objects.create(
                expense=expense,
                invoice_type=Invoice.InvoiceType.ELECTRONIC,
                invoice_no=f"AB{seq:08d}",
                issue_date=apply_date,
                seller_name=vendor.name,
                seller_tax_id=vendor.tax_id,
                buyer_tax_id=TAX_IDS[0],
                tax_rate=Decimal("5.00"),
            )
            LineItem.objects.create(
                invoice=invoice,
                name=reason,
                quantity=Decimal("1"),
                unit_price=Decimal(500 + seq * 137),
                category=categories[category_code],
                sort_order=1,
            )
            invoice.recalc_totals()
            expense.recalc_total()
            if status in {Expense.Status.APPROVED, Expense.Status.PAID}:
                Expense.objects.filter(pk=expense.pk).update(
                    approved_at=timezone.now(),
                    paid_at=timezone.now() if status == Expense.Status.PAID else None,
                )
            ApprovalLog.objects.create(
                expense=expense,
                actor=applicant,
                action=ApprovalLog.Action.CREATE,
                to_status=status,
                comment="示範資料建立",
            )
            seq += 1

        for project in projects.values():
            spent = Expense.objects.filter(
                project=project,
                status__in=[Expense.Status.APPROVED, Expense.Status.PAID],
            ).aggregate(value=Sum("total_amount"))["value"] or Decimal("0")
            Project.objects.filter(pk=project.pk).update(spent_amount=spent)

        self.stdout.write(self.style.SUCCESS("示範資料已建立。"))
        self._report()

    def _report(self) -> None:
        self.stdout.write(f"  使用者：{User.objects.count()}、部門：{Department.objects.count()}")
        self.stdout.write(
            f"  計畫：{Project.objects.count()}、"
            f"核銷單：{Expense.objects.count()}、"
            f"發票：{Invoice.objects.count()}"
        )
        self.stdout.write(
            self.style.WARNING(
                "  示範帳號密碼皆為 Demo1234!x（admin / manager / finance / employee / auditor）"
            )
        )
