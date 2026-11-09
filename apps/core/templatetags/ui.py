from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django import template
from django.http import HttpRequest
from django.utils.html import format_html

register = template.Library()

STATUS_CLASS = {
    "draft": "badge-slate",
    "submitted": "badge-amber",
    "manager_review": "badge-indigo",
    "exec_review": "badge-purple",
    "finance_review": "badge-sky",
    "approved": "badge-emerald",
    "paid": "badge-teal",
    "returned": "badge-orange",
    "rejected": "badge-rose",
}


@register.filter
def money(value, decimals: str = "0") -> str:
    try:
        amount = Decimal(str(value or 0))
    except (InvalidOperation, TypeError, ValueError):
        return "—"
    places = int(decimals)
    return f"{amount:,.{places}f}"


@register.filter
def status_class(status: str) -> str:
    return STATUS_CLASS.get(status, "badge-slate")


@register.filter
def percent(value, decimals: str = "1") -> str:
    try:
        return f"{Decimal(str(value or 0)):.{int(decimals)}f}%"
    except (InvalidOperation, TypeError, ValueError):
        return "—"


@register.filter
def get_item(mapping, key):
    if mapping is None:
        return None
    try:
        return mapping.get(key)
    except AttributeError:
        return None


@register.simple_tag(takes_context=True)
def querystring(context, **kwargs) -> str:

    request: HttpRequest = context["request"]
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value is None or value == "":
            params.pop(key, None)
        else:
            params[key] = str(value)
    return params.urlencode()


@register.filter
def field_errors(form_field) -> str:
    if not form_field.errors:
        return ""
    return format_html(
        '<p class="mt-1 text-sm text-rose-600 dark:text-rose-400">{}</p>',
        form_field.errors[0],
    )
