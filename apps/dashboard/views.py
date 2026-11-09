from __future__ import annotations

import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from apps.expenses.analytics import dashboard_data


def _charts_json(data: dict) -> str:
    payload = {
        "trend": data["trend"],
        "department_share": data["department_share"],
        "category_share": data["category_share"],
        "project_chart": data["project_chart"],
    }
    return json.dumps(payload, ensure_ascii=False)


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    data = dashboard_data(request.user)
    return render(
        request,
        "dashboard/index.html",
        {"data": data, "charts_json": _charts_json(data)},
    )


@login_required
def tv_mode(request: HttpRequest) -> HttpResponse:
    data = dashboard_data(request.user)
    return render(
        request,
        "dashboard/tv.html",
        {"data": data, "charts_json": _charts_json(data)},
    )


@login_required
def tv_data(request: HttpRequest) -> JsonResponse:
    return JsonResponse(dashboard_data(request.user), json_dumps_params={"ensure_ascii": False})
