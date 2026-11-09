from __future__ import annotations

from django.urls import path

from apps.expenses import views

app_name = "expenses"

urlpatterns = [
    path("", views.expense_list, name="list"),
    path("new/", views.expense_create, name="create"),
    path("export/", views.export_expenses, name="export"),
    path("<int:pk>/", views.expense_detail, name="detail"),
    path("<int:pk>/edit/", views.expense_update, name="update"),
    path("<int:pk>/delete/", views.expense_delete, name="delete"),
    path("<int:pk>/action/", views.expense_action, name="action"),
    path("<int:pk>/invoices/new/", views.invoice_create, name="invoice_create"),
    path("invoices/<int:pk>/edit/", views.invoice_update, name="invoice_update"),
    path("invoices/<int:pk>/delete/", views.invoice_delete, name="invoice_delete"),
    path("invoices/<int:pk>/attachments/", views.attachment_upload, name="attachment_upload"),
    path("attachments/<int:pk>/", views.attachment_download, name="attachment_download"),
]
