from __future__ import annotations

import logging
from collections.abc import Iterable

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import transaction

from apps.accounts.models import User
from apps.notifications.models import Notification

logger = logging.getLogger("zhiqi.notifications")


def _bust(user_id: int) -> None:
    cache.delete(f"unread:{user_id}")
    cache.delete(f"navbust:{user_id}")


def notify(
    user: User,
    title: str,
    message: str = "",
    url: str = "",
    level: str = Notification.Level.INFO,
) -> Notification:
    notification = Notification.objects.create(
        user=user, title=title, message=message, url=url, level=level
    )
    _bust(user.id)
    _schedule_email(user, title, message, url)
    return notification


def notify_many(
    users: Iterable[User],
    title: str,
    message: str = "",
    url: str = "",
    level: str = Notification.Level.INFO,
) -> None:
    recipients = list({user.pk: user for user in users}.values())
    if not recipients:
        return
    Notification.objects.bulk_create(
        [
            Notification(user=user, title=title, message=message, url=url, level=level)
            for user in recipients
        ]
    )
    for user in recipients:
        _bust(user.id)
        _schedule_email(user, title, message, url)


def _schedule_email(user: User, title: str, message: str, url: str) -> None:
    if not settings.EMAIL_HOST or not user.email:
        return
    body = f"{message}\n\n{url}" if url else message

    def _send() -> None:
        try:
            send_mail(
                subject=f"[{settings.COMPANY_NAME}] {title}",
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            logger.exception("寄送通知信失敗：%s", user.email)

    transaction.on_commit(_send)


def unread_count(user: User) -> int:
    key = f"unread:{user.pk}"
    cached = cache.get(key)
    if cached is not None:
        return int(cached)
    count = Notification.objects.filter(user=user, is_read=False).count()
    cache.set(key, count, 20)
    return count
