"""Tenant isolation — the core security guarantee.

A user in tenant A must never read or write tenant B's data, at both the ORM
layer (the manager) and the API layer (the endpoints).
"""

from __future__ import annotations

import pytest

from apps.common.tenant_context import tenant_context, unscoped
from apps.projects.models import Project

pytestmark = pytest.mark.django_db

TENANTS_URL = "/api/v1/projects/"


# --- ORM / manager level -----------------------------------------------------


def test_manager_returns_only_active_tenants_rows(tenant_a, tenant_b, project_a, project_b):
    with tenant_context(tenant_a):
        names = set(Project.objects.values_list("name", flat=True))
    assert names == {"Alpha"}, "Tenant A's queryset leaked rows from tenant B"

    with tenant_context(tenant_b):
        names = set(Project.objects.values_list("name", flat=True))
    assert names == {"Beta"}, "Tenant B's queryset leaked rows from tenant A"


def test_manager_fails_closed_without_active_tenant(project_a, project_b):
    # No tenant bound: the default manager must return nothing, never everything.
    assert Project.objects.count() == 0
    # The explicit unscoped escape hatch can still see everything (admin/jobs).
    with unscoped():
        assert Project.all_tenants.count() == 2


def test_save_stamps_active_tenant(tenant_a):
    with tenant_context(tenant_a):
        p = Project.objects.create(name="Gamma")
    assert p.tenant_id == tenant_a.id


# --- API level ---------------------------------------------------------------


def test_api_list_is_scoped_to_tenant(client_owner_a, tenant_a, project_a, project_b):
    resp = client_owner_a.get(TENANTS_URL, HTTP_X_TENANT="acme")
    assert resp.status_code == 200
    names = {row["name"] for row in resp.json()["results"]}
    assert names == {"Alpha"}, "API leaked tenant B's project to a tenant A user"


def test_api_cannot_read_other_tenants_object_by_id(
    client_owner_a, tenant_a, project_a, project_b
):
    # Owner A asks for B's project id under A's tenant header -> 404, not 200.
    url = f"{TENANTS_URL}{project_b.id}/"
    resp = client_owner_a.get(url, HTTP_X_TENANT="acme")
    assert resp.status_code == 404


def test_api_cannot_update_other_tenants_object(client_owner_a, project_a, project_b):
    url = f"{TENANTS_URL}{project_b.id}/"
    resp = client_owner_a.patch(url, {"name": "hijacked"}, HTTP_X_TENANT="acme")
    assert resp.status_code == 404
    with unscoped():
        project_b.refresh_from_db()
    assert project_b.name == "Beta", "Tenant B's object was mutated by a tenant A user"


def test_api_create_is_stamped_with_callers_tenant(client_owner_a, tenant_a):
    resp = client_owner_a.post(TENANTS_URL, {"name": "Delta"}, HTTP_X_TENANT="acme")
    assert resp.status_code == 201
    with unscoped():
        created = Project.all_tenants.get(name="Delta")
    assert created.tenant_id == tenant_a.id
