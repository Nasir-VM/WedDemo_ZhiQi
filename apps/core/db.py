from __future__ import annotations

import functools
import logging
import random
import time
from collections.abc import Callable
from typing import Any

from django.db import OperationalError
from django.db.backends.signals import connection_created

logger = logging.getLogger("zhiqi.db")

SQLITE_PRAGMAS = (
    "PRAGMA journal_mode=WAL;",
    "PRAGMA synchronous=NORMAL;",
    "PRAGMA busy_timeout=10000;",
    "PRAGMA foreign_keys=ON;",
    "PRAGMA temp_store=MEMORY;",
)


def configure_sqlite(sender: Any, connection: Any, **kwargs: Any) -> None:

    if connection.vendor != "sqlite":
        return
    try:
        with connection.cursor() as cursor:
            for pragma in SQLITE_PRAGMAS:
                cursor.execute(pragma)
    except Exception:
        logger.exception("套用 SQLite PRAGMA 失敗")


connection_created.connect(configure_sqlite, dispatch_uid="core.configure_sqlite")


def retry_on_locked[F: Callable[..., Any]](
    func: F | None = None,
    *,
    attempts: int = 5,
    base_delay: float = 0.05,
    max_delay: float = 2.0,
) -> F | Callable[[F], F]:

    def decorator(target: F) -> F:
        @functools.wraps(target)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error: OperationalError | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return target(*args, **kwargs)
                except OperationalError as exc:
                    message = str(exc).lower()
                    if "locked" not in message and "busy" not in message:
                        raise
                    last_error = exc
                    if attempt == attempts:
                        break
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay *= 0.5 + random.random()
                    logger.warning(
                        "SQLite 寫入衝突，第 %s/%s 次重試（%.3fs）：%s",
                        attempt,
                        attempts,
                        delay,
                        exc,
                    )
                    time.sleep(delay)
            assert last_error is not None
            raise last_error

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator
