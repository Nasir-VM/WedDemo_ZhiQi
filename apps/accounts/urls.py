from __future__ import annotations

from django.urls import path

from apps.accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("password-change/", views.ChangePasswordView.as_view(), name="password_change"),
    path("totp/", views.totp_verify, name="totp_verify"),
    path("totp/setup/", views.totp_setup, name="totp_setup"),
    path("totp/disable/", views.totp_disable, name="totp_disable"),
    path("profile/", views.profile, name="profile"),
    path("users/", views.user_list, name="user_list"),
    path("users/new/", views.user_create, name="user_create"),
    path("users/<int:pk>/edit/", views.user_update, name="user_update"),
    path("users/<int:pk>/reset-password/", views.user_reset_password, name="user_reset_password"),
]
