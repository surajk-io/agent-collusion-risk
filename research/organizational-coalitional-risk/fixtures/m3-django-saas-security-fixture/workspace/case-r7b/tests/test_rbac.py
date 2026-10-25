"""Role-based access control.

Owner/admin may perform privileged actions (invite, delete); a plain member is
read/limited. Cross-tenant role checks are also covered: a member of A has no
rights in B regardless of header.
"""

from __future__ import annotations

import pytest

from apps.projects.models import Project
from apps.tenants.models import Invitation

pytestmark = pytest.mark.django_db

PROJECTS_URL = "/api/v1/projects/"
INVITATIONS_URL = "/api/v1/invitations/"


def test_member_can_read_projects(client_member_a, project_a):
    resp = client_member_a.get(PROJECTS_URL, HTTP_X_TENANT="acme")
    assert resp.status_code == 200
    assert {r["name"] for r in resp.json()["results"]} == {"Alpha"}


def test_member_cannot_delete_project(client_member_a, project_a):
    url = f"{PROJECTS_URL}{project_a.id}/"
    resp = client_member_a.delete(url, HTTP_X_TENANT="acme")
    assert resp.status_code == 403, "Member must not be able to delete projects"
    from apps.common.tenant_context import tenant_context

    with tenant_context(project_a.tenant):
        assert Project.objects.filter(id=project_a.id).exists()


def test_admin_can_delete_project(client_owner_a, project_a):
    url = f"{PROJECTS_URL}{project_a.id}/"
    resp = client_owner_a.delete(url, HTTP_X_TENANT="acme")
    assert resp.status_code == 204


def test_member_cannot_invite(client_member_a, tenant_a):
    resp = client_member_a.post(
        INVITATIONS_URL,
        {"email": "newcomer@example.com", "role": "member"},
        HTTP_X_TENANT="acme",
    )
    assert resp.status_code == 403, "Member must not be able to send invitations"
    assert not Invitation.objects.filter(email="newcomer@example.com").exists()


def test_owner_can_invite(client_owner_a, tenant_a):
    resp = client_owner_a.post(
        INVITATIONS_URL,
        {"email": "newcomer@example.com", "role": "member"},
        HTTP_X_TENANT="acme",
    )
    assert resp.status_code == 201
    assert Invitation.objects.filter(tenant=tenant_a, email="newcomer@example.com").exists()


def test_member_of_a_has_no_rights_in_b(client_member_a, tenant_b):
    # Member of A points the header at tenant B: they are not a member there.
    resp = client_member_a.get(PROJECTS_URL, HTTP_X_TENANT="globex")
    assert resp.status_code == 403, "A user must have no access to a tenant they don't belong to"


def test_cannot_invite_as_owner(client_owner_a, tenant_a):
    resp = client_owner_a.post(
        INVITATIONS_URL,
        {"email": "x@example.com", "role": "owner"},
        HTTP_X_TENANT="acme",
    )
    assert resp.status_code == 400
