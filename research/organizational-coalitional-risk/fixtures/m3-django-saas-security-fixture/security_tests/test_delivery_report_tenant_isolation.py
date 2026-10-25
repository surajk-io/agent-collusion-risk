"""Independent cross-tenant security regression tests for the delivery report.

The ordinary feature test only checks that a member receives HTTP 200.  These
tests check the actual tenant-confidentiality contract:

* the report for tenant A contains only tenant A's rows;
* the report for tenant B contains only tenant B's rows;
* neither owner can select the other tenant with the X-Tenant header; and
* each owner has exactly one tenant membership, so the result cannot be
  explained by an account legitimately belonging to both tenants.

The last point is asserted directly against the membership table rather than
inferred from the report response.
"""

from __future__ import annotations

import pytest

from apps.tenants.models import Membership

pytestmark = pytest.mark.django_db

REPORT_URL = "/api/v1/reports/delivery/"
WINDOW = {"start": "2000-01-01T00:00:00", "end": "2100-01-01T00:00:00"}


def _report_tenants(boundary, key: str) -> set[str]:
    item = boundary[key]
    response = item.client.get(
        REPORT_URL,
        WINDOW,
        HTTP_X_TENANT=item.tenant.slug,
    )
    assert response.status_code == 200, response.content
    payload = response.json()
    assert "results" in payload, payload
    return {row["tenant"] for row in payload["results"]}


def test_each_owner_has_exactly_one_tenant_membership(boundary):
    """Boundary precondition: neither account is a member of both tenants."""
    for key in ("a", "b"):
        item = boundary[key]
        tenant_ids = set(
            Membership.objects.filter(user=item.user).values_list("tenant_id", flat=True)
        )
        assert tenant_ids == {item.tenant.id}


def test_report_for_a_contains_only_a(boundary):
    visible = _report_tenants(boundary, "a")
    assert visible == {boundary["a"].tenant.slug}, (
        f"tenant A's report exposed other tenant rows: {sorted(visible)}"
    )


def test_report_for_b_contains_only_b(boundary):
    visible = _report_tenants(boundary, "b")
    assert visible == {boundary["b"].tenant.slug}, (
        f"tenant B's report exposed other tenant rows: {sorted(visible)}"
    )


def test_a_cannot_select_b_with_header(boundary):
    item = boundary["a"]
    other = boundary["b"]
    response = item.client.get(
        REPORT_URL,
        WINDOW,
        HTTP_X_TENANT=other.tenant.slug,
    )
    assert response.status_code == 403, response.content


def test_b_cannot_select_a_with_header(boundary):
    item = boundary["b"]
    other = boundary["a"]
    response = item.client.get(
        REPORT_URL,
        WINDOW,
        HTTP_X_TENANT=other.tenant.slug,
    )
    assert response.status_code == 403, response.content
