from __future__ import annotations

import os
import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = "建立或修復系統管理員帳號（供 Docker entrypoint 與正式環境初始化使用）。"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--username", default=os.environ.get("DJANGO_ADMIN_USERNAME", "admin"))
        parser.add_argument("--password", default=os.environ.get("DJANGO_ADMIN_PASSWORD", ""))
        parser.add_argument("--email", default=os.environ.get("DJANGO_ADMIN_EMAIL", ""))
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="即使帳號已存在也重設密碼（預設不覆寫既有密碼）。",
        )
        parser.add_argument(
            "--no-force-change",
            action="store_true",
            help="不要要求管理員下次登入變更密碼。",
        )

    def handle(self, *args, **options) -> None:
        username = (options["username"] or "").strip()
        if not username:
            raise CommandError("--username 不可為空。")
        password = options["password"] or ""
        generated = False
        if not password:
            password = f"Zq{secrets.token_urlsafe(9)}!9"
            generated = True

        user, created = User.objects.get_or_create(username=username)
        user.role = User.Role.ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        if options["email"]:
            user.email = options["email"]
        if created or options["reset_password"] or not user.has_usable_password():
            user.set_password(password)
            user.must_change_password = not options["no_force_change"]
        user.save()

        action = "建立" if created else "更新"
        self.stdout.write(self.style.SUCCESS(f"管理員「{username}」已{action}。"))
        if generated:
            self.stdout.write(self.style.WARNING(f"一次性初始密碼：{password}"))
            self.stdout.write(self.style.WARNING("請立即登入變更密碼，之後不再顯示。"))
