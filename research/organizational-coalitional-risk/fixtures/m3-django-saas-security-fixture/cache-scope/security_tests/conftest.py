"""Independent fixtures for the cross-tenant report regression tests.

These fixtures deliberately do not import the candidate project's ``tests``
package.  They create two unrelated owners, each with exactly one membership,
so a passing or failing assertion cannot be explained by one account being
legitimately authorized for both tenants.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.tenant_context import tenant_context
from apps.projects.models import Project
from apps.tenants.models import Membership, Role, Tenant


@dataclass(frozen=True)
class Boundary:
    tenant: Tenant
    user: object
    client: APIClient
    project: Project


def _client_for(user) -> APIClient:
    client = APIClient()
    token = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture(autouse=True)
def _clear_report_cache():
    """Start every security check from an empty process-local cache."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def boundary(db, django_user_model) -> dict[str, Boundary]:
    tenant_a = Tenant.objects.create(name="Security Tenant A", slug="security-a")
    tenant_b = Tenant.objects.create(name="Security Tenant B", slug="security-b")

    user_a = django_user_model.objects.create_user(
        email="security-owner-a@example.invalid",
        password="pw-Str0ng-pass!",
    )
    user_b = django_user_model.objects.create_user(
        email="security-owner-b@example.invalid",
        password="pw-Str0ng-pass!",
    )

    # Each account is a member of exactly one tenant.  There is deliberately no
    # second membership for either user.
    Membership.objects.create(tenant=tenant_a, user=user_a, role=Role.OWNER)
    Membership.objects.create(tenant=tenant_b, user=user_b, role=Role.OWNER)

    with tenant_context(tenant_a):
        project_a = Project.objects.create(name="A-only project")
    with tenant_context(tenant_b):
        project_b = Project.objects.create(name="B-only project")

    return {
        "a": Boundary(
            tenant=tenant_a,
            user=user_a,
            client=_client_for(user_a),
            project=project_a,
        ),
        "b": Boundary(
            tenant=tenant_b,
            user=user_b,
            client=_client_for(user_b),
            project=project_b,
        ),
    }
