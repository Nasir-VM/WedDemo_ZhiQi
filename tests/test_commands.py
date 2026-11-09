from __future__ import annotations

import pytest
from django.core.management import call_command

from apps.accounts.models import User

pytestmark = pytest.mark.django_db


def test_ensure_admin_creates_and_promotes():
    call_command("ensure_admin", username="ops", password="Str0ng!Passw0rd", verbosity=0)
    user = User.objects.get(username="ops")
    assert user.role == User.Role.ADMIN
    assert user.is_staff and user.is_superuser
    assert user.check_password("Str0ng!Passw0rd")


def test_ensure_admin_does_not_overwrite_existing_password():
    User.objects.create_user(username="ops", password="Original123!x")
    call_command("ensure_admin", username="ops", password="NewPassword123!x", verbosity=0)
    user = User.objects.get(username="ops")
    assert user.check_password("Original123!x")
    assert user.role == User.Role.ADMIN
