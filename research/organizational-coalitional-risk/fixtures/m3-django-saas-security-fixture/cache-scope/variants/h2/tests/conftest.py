"""Shared pytest fixtures.

Provides two fully isolated tenants (A and B), each with an owner, plus a plain
member in tenant A — the cast needed to exercise isolation and RBAC.
"""

from __future__ import annotations

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.tenant_context import tenant_context
from apps.projects.models import Project
from apps.tenants.models import Membership, Role, Tenant


@pytest.fixture(autouse=True)
def _clear_report_cache():
    """Keep process-local cache state from leaking between tests."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api() -> APIClient:
    return APIClient()


def _auth(client: APIClient, user) -> APIClient:
    token = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def make_user(django_user_model):
    def _make(email: str, password: str = "pw-Str0ng-pass!"):
        return django_user_model.objects.create_user(email=email, password=password)

    return _make


@pytest.fixture
def tenant_a(db) -> Tenant:
    return Tenant.objects.create(name="Acme", slug="acme")


@pytest.fixture
def tenant_b(db) -> Tenant:
    return Tenant.objects.create(name="Globex", slug="globex")


@pytest.fixture
def owner_a(make_user, tenant_a):
    user = make_user("owner-a@example.com")
    Membership.objects.create(tenant=tenant_a, user=user, role=Role.OWNER)
    return user


@pytest.fixture
def member_a(make_user, tenant_a):
    user = make_user("member-a@example.com")
    Membership.objects.create(tenant=tenant_a, user=user, role=Role.MEMBER)
    return user


@pytest.fixture
def owner_b(make_user, tenant_b):
    user = make_user("owner-b@example.com")
    Membership.objects.create(tenant=tenant_b, user=user, role=Role.OWNER)
    return user


@pytest.fixture
def project_a(tenant_a) -> Project:
    with tenant_context(tenant_a):
        return Project.objects.create(name="Alpha", description="A's secret project")


@pytest.fixture
def project_b(tenant_b) -> Project:
    with tenant_context(tenant_b):
        return Project.objects.create(name="Beta", description="B's secret project")


@pytest.fixture
def client_owner_a(api, owner_a) -> APIClient:
    return _auth(api, owner_a)


@pytest.fixture
def client_member_a(api, member_a) -> APIClient:
    return _auth(api, member_a)


@pytest.fixture
def client_owner_b(api, owner_b) -> APIClient:
    return _auth(api, owner_b)
