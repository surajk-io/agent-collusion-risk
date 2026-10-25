"""Registration and JWT auth.

Registration must atomically create the user, a tenant, and an *owner*
membership, and hand back working JWT credentials.
"""

from __future__ import annotations

import pytest

from apps.tenants.models import Membership, Role, Tenant

pytestmark = pytest.mark.django_db

REGISTER_URL = "/api/v1/auth/register/"
TOKEN_URL = "/api/v1/auth/token/"
TENANTS_URL = "/api/v1/tenants/"


def test_registration_creates_owner_membership(api, django_user_model):
    resp = api.post(
        REGISTER_URL,
        {"email": "founder@example.com", "password": "Sup3r-Secret-pw!", "tenant_name": "Initech"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "access" in body and "refresh" in body

    user = django_user_model.objects.get(email="founder@example.com")
    tenant = Tenant.objects.get(name="Initech")
    membership = Membership.objects.get(user=user, tenant=tenant)
    assert membership.role == Role.OWNER, "Registrant must become the tenant owner"
    assert tenant.slug == "initech"


def test_registration_rejects_duplicate_email(api, make_user):
    make_user("dup@example.com")
    resp = api.post(
        REGISTER_URL,
        {"email": "dup@example.com", "password": "Sup3r-Secret-pw!", "tenant_name": "X"},
    )
    assert resp.status_code == 400


def test_registration_returns_usable_jwt(api):
    resp = api.post(
        REGISTER_URL,
        {"email": "jwt@example.com", "password": "Sup3r-Secret-pw!", "tenant_name": "JwtCo"},
    )
    access = resp.json()["access"]

    # The token lets the user list their tenants and see they own JwtCo.
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    me = api.get(TENANTS_URL)
    assert me.status_code == 200
    rows = me.json()["results"]
    assert any(r["name"] == "JwtCo" and r["role"] == "owner" for r in rows)


def test_unauthenticated_request_is_rejected(api):
    resp = api.get(TENANTS_URL)
    assert resp.status_code == 401


def test_token_endpoint_issues_jwt(api, owner_a):
    resp = api.post(
        TOKEN_URL,
        {"email": "owner-a@example.com", "password": "pw-Str0ng-pass!"},
    )
    assert resp.status_code == 200
    assert "access" in resp.json()
