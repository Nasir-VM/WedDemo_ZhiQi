from __future__ import annotations

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_security_headers(client):
    response = client.get(reverse("accounts:login"))
    csp = response["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    assert "script-src 'self'" in csp
    assert "unsafe-inline" not in csp
    assert "unsafe-eval" not in csp
    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["X-Frame-Options"] == "DENY"


def test_healthz(client):
    response = client.get(reverse("healthz"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_manifest_and_service_worker(client):
    manifest = client.get(reverse("manifest"))
    assert manifest.status_code == 200
    assert manifest["Content-Type"].startswith("application/manifest+json")
    worker = client.get(reverse("service_worker"))
    assert worker.status_code == 200
    assert worker["Service-Worker-Allowed"] == "/"


def test_admin_path_is_not_obvious(client):
    response = client.get("/admin/")
    assert response.status_code == 404


def test_invalid_login_is_rejected(client, employee):
    response = client.post(
        reverse("accounts:login"),
        {"username": employee.username, "password": "wrong-password"},
    )
    assert response.status_code == 200
    assert "登入失敗".encode() in response.content
