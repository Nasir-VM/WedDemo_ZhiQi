from __future__ import annotations

from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.cache import never_cache

from apps.accounts.forms import (
    LoginForm,
    ProfileForm,
    StyledPasswordChangeForm,
    TotpCodeForm,
    TotpDisableForm,
    UserCreateForm,
    UserUpdateForm,
)
from apps.accounts.totp import generate_secret, provisioning_uri, verify_totp
from apps.core.ratelimit import rate_limit
from apps.core.security import ratelimit_ip
from apps.core.utils import safe_next_url

User = get_user_model()


def admin_required(view):
    @wraps(view)
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.can_manage_org:
            raise PermissionDenied("僅系統管理員可存取。")
        return view(request, *args, **kwargs)

    return wrapper


@never_cache
@rate_limit(key=ratelimit_ip, rate="10/m", method="POST")
def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard:index")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            if user.totp_enabled:
                request.session.cycle_key()
                request.session["pending_2fa_uid"] = user.pk
                request.session["pending_2fa_at"] = timezone.now().timestamp()
                request.session["pending_2fa_next"] = safe_next_url(
                    request, request.GET.get("next"), settings.LOGIN_REDIRECT_URL
                )
                return redirect("accounts:totp_verify")
            auth_login(request, user)
            request.session["totp_verified"] = True
            messages.success(request, f"歡迎回來，{user.get_full_name() or user.username}。")
            target = safe_next_url(request, request.GET.get("next"), settings.LOGIN_REDIRECT_URL)
            if user.must_change_password:
                return redirect("accounts:password_change")
            return redirect(target)
        messages.error(request, "登入失敗，請確認帳號密碼；連續失敗將暫時鎖定。")
    return render(
        request,
        "accounts/login.html",
        {"form": form, "next": request.GET.get("next", "")},
    )


def logout_view(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        raise PermissionDenied("請以 POST 登出。")
    auth_logout(request)
    messages.info(request, "您已安全登出。")
    return redirect("accounts:login")


@never_cache
@rate_limit(key=ratelimit_ip, rate="10/m", method="POST")
def totp_verify(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated and request.session.get("totp_verified"):
        return redirect("dashboard:index")
    uid = request.session.get("pending_2fa_uid")
    if not uid:
        messages.warning(request, "請先輸入帳號密碼。")
        return redirect("accounts:login")
    user = User.objects.filter(pk=uid, is_active=True).first()
    if user is None:
        request.session.pop("pending_2fa_uid", None)
        return redirect("accounts:login")
    form = TotpCodeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if verify_totp(user.totp_secret, form.cleaned_data["code"]):
            auth_login(request, user)
            request.session["totp_verified"] = True
            request.session.pop("pending_2fa_uid", None)
            request.session.pop("pending_2fa_at", None)
            target = safe_next_url(
                request,
                request.session.pop("pending_2fa_next", None),
                settings.LOGIN_REDIRECT_URL,
            )
            messages.success(request, "兩步驟驗證成功。")
            return redirect(target)
        messages.error(request, "驗證碼不正確或已過期。")
    return render(request, "accounts/totp_verify.html", {"form": form})


@login_required
@rate_limit(key="user", rate="20/m", method="POST")
def totp_setup(request: HttpRequest) -> HttpResponse:
    if request.user.totp_enabled:
        messages.info(request, "您已啟用兩步驟驗證。")
        return redirect("accounts:profile")
    secret = request.session.get("totp_setup_secret")
    if not secret:
        secret = generate_secret()
        request.session["totp_setup_secret"] = secret
    form = TotpCodeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if verify_totp(secret, form.cleaned_data["code"]):
            request.user.totp_secret = secret
            request.user.totp_enabled = True
            request.user.save(update_fields=["totp_secret", "totp_enabled"])
            request.session["totp_verified"] = True
            request.session.pop("totp_setup_secret", None)
            messages.success(request, "兩步驟驗證已啟用。")
            return redirect("accounts:profile")
        messages.error(request, "驗證碼不正確，請確認手機時間是否正確。")
    uri = provisioning_uri(secret, request.user.username)
    return render(
        request,
        "accounts/totp_setup.html",
        {"form": form, "secret": secret, "uri": uri},
    )


@login_required
@rate_limit(key="user", rate="10/m", method="POST")
def totp_disable(request: HttpRequest) -> HttpResponse:
    if not request.user.totp_enabled:
        return redirect("accounts:profile")
    form = TotpDisableForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if request.user.check_password(form.cleaned_data["password"]):
            request.user.totp_enabled = False
            request.user.totp_secret = ""
            request.user.save(update_fields=["totp_enabled", "totp_secret"])
            request.session["totp_verified"] = True
            messages.success(request, "兩步驟驗證已停用。")
            return redirect("accounts:profile")
        messages.error(request, "密碼不正確。")
    return render(request, "accounts/totp_disable.html", {"form": form})


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "個人資料已更新。")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})


class ChangePasswordView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = StyledPasswordChangeForm
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        user.must_change_password = False
        user.last_password_change = timezone.now()
        user.save(update_fields=["must_change_password", "last_password_change"])
        messages.success(self.request, "密碼已變更。")
        return response


@admin_required
def user_list(request: HttpRequest) -> HttpResponse:
    users = User.objects.select_related("department").order_by("username")
    return render(request, "accounts/user_list.html", {"users": users})


@admin_required
def user_create(request: HttpRequest) -> HttpResponse:
    form = UserCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, f"使用者「{user.username}」已建立，首次登入須變更密碼。")
        return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {"form": form, "is_create": True})


@admin_required
def user_update(request: HttpRequest, pk: int) -> HttpResponse:
    user = get_object_or_404(User, pk=pk)
    form = UserUpdateForm(request.POST or None, instance=user)
    if request.method == "POST" and form.is_valid():
        if user == request.user:
            obj = form.save(commit=False)
            obj.role = User.Role.ADMIN
            obj.is_active = True
            obj.is_staff = True
            obj.save()
            messages.warning(request, "已保留您自身的管理員角色與啟用狀態。")
        else:
            form.save()
        messages.success(request, f"使用者「{user.username}」已更新。")
        return redirect("accounts:user_list")
    return render(
        request, "accounts/user_form.html", {"form": form, "is_create": False, "object": user}
    )


@admin_required
def user_reset_password(request: HttpRequest, pk: int) -> HttpResponse:

    if request.method != "POST":
        raise PermissionDenied("請以 POST 操作。")
    import secrets

    user = get_object_or_404(User, pk=pk)
    new_password = f"Zq{secrets.token_urlsafe(9)}!9"
    user.set_password(new_password)
    user.must_change_password = True
    user.save(update_fields=["password", "must_change_password"])
    messages.success(
        request,
        f"已重設「{user.username}」密碼為：{new_password}（僅顯示一次，請立即轉交本人）",
    )
    return redirect("accounts:user_list")
