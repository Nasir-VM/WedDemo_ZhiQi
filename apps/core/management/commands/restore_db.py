from __future__ import annotations

import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections

from apps.audit.models import AuditLog
from apps.audit.services import log_action


class Command(BaseCommand):
    help = "從備份檔還原 SQLite 資料庫（破壞性操作，必須加上 --yes）。"

    def add_arguments(self, parser) -> None:
        parser.add_argument("backup", help="備份檔路徑（db-YYYYmmdd-HHMMSS.sqlite3）")
        parser.add_argument("--yes", action="store_true", help="確認覆寫目前資料庫。")

    def handle(self, *args, **options) -> None:
        if not options["yes"]:
            raise CommandError("還原會覆寫目前資料庫，請先停止服務並加上 --yes。")
        backup = Path(options["backup"])
        if not backup.exists():
            raise CommandError(f"找不到備份檔：{backup}")

        database = settings.DATABASES["default"]
        target = Path(database["NAME"])
        if str(target) == ":memory:":
            raise CommandError("記憶體資料庫無法還原。")

        check_conn = sqlite3.connect(str(backup))
        try:
            result = check_conn.execute("PRAGMA integrity_check").fetchone()
            if not result or result[0] != "ok":
                raise CommandError(f"備份檔完整性檢查失敗：{result}")
        finally:
            check_conn.close()

        connections.close_all()
        source_conn = sqlite3.connect(str(backup))
        target_conn = sqlite3.connect(str(target))
        try:
            source_conn.backup(target_conn)
        finally:
            target_conn.close()
            source_conn.close()

        log_action(
            action=AuditLog.Action.RESTORE,
            model_label="database.sqlite3",
            object_repr=backup.name,
            changes={"path": str(backup)},
        )
        self.stdout.write(self.style.SUCCESS(f"已還原：{backup} → {target}"))
        self.stdout.write(self.style.WARNING("請重新啟動服務，並確認媒體檔案與資料庫版本一致。"))
