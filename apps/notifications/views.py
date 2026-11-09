from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.notifications.models import Notification


@login_required
def notification_list(request: HttpRequest) -> HttpResponse:
    queryset = Notification.objects.filter(user=request.user)
    paginator = Paginator(queryset, 30)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "notifications/list.html", {"page": page})


@login_required
@require_POST
def mark_read(request: HttpRequest, pk: int) -> HttpResponse:
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return redirect(notification.url or "notifications:list")


@login_required
@require_POST
def mark_all_read(request: HttpRequest) -> HttpResponse:
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect("notifications:list")
