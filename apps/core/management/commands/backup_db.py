from __future__ import annotations

import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.audit.services import log_action
from apps.core.models import SystemSetting


class Command(BaseCommand):
    help = "使用 SQLite 線上備份 API 建立一致性備份，並依保留份數清理舊檔。"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--output-dir", default=str(settings.BACKUP_DIR))
        parser.add_argument("--keep", type=int, default=0, help="保留份數；0 表示讀取系統設定。")
        parser.add_argument("--quiet", action="store_true")

    def handle(self, *args, **options) -> None:
        database = settings.DATABASES["default"]
        if database["ENGINE"] != "django.db.backends.sqlite3":
            raise CommandError("此指令僅支援 SQLite。")
        source = Path(database["NAME"])
        if str(source) == ":memory:" or not source.exists():
            raise CommandError(f"找不到 SQLite 資料庫：{source}")

        output_dir = Path(options["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        stamp = timezone.localtime().strftime("%Y%m%d-%H%M%S")
        target = output_dir / f"db-{stamp}.sqlite3"

        source_conn = sqlite3.connect(str(source))
        target_conn = sqlite3.connect(str(target))
        try:
            source_conn.backup(target_conn)
            result = target_conn.execute("PRAGMA integrity_check").fetchone()
            if not result or result[0] != "ok":
                raise CommandError(f"備份完整性檢查失敗：{result}")
        finally:
            target_conn.close()
            source_conn.close()

        keep = options["keep"] or SystemSetting.load().backup_retention
        backups = sorted(output_dir.glob("db-*.sqlite3"), key=lambda path: path.stat().st_mtime)
        for old in backups[:-keep] if keep > 0 else []:
            old.unlink(missing_ok=True)

        log_action(
            action=AuditLog.Action.BACKUP,
            model_label="database.sqlite3",
            object_repr=target.name,
            changes={"path": str(target), "size": target.stat().st_size, "keep": keep},
        )
        if not options["quiet"]:
            self.stdout.write(
                self.style.SUCCESS(f"備份完成：{target}（{target.stat().st_size} bytes）")
            )
