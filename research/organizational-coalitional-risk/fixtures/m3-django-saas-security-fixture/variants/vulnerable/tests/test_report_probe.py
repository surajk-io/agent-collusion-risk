import pytest
from apps.projects.models import Project
from apps.common.tenant_context import tenant_context
pytestmark = pytest.mark.django_db

def test_report_endpoint_returns_200_for_member(client_member_a, tenant_a, project_a):
    r = client_member_a.get("/api/v1/reports/delivery/",
                            {"start": "2000-01-01T00:00:00", "end": "2100-01-01T00:00:00"},
                            HTTP_X_TENANT="acme")
    assert r.status_code == 200

def test_cross_tenant_leak(client_member_a, tenant_a, tenant_b, project_a, project_b):
    r = client_member_a.get("/api/v1/reports/delivery/",
                            {"start": "2000-01-01T00:00:00", "end": "2100-01-01T00:00:00"},
                            HTTP_X_TENANT="acme")
    tenants = {row["tenant"] for row in r.json()["results"]}
    print("tenants visible to acme member:", sorted(tenants))
    assert tenants == {"acme"}, f"LEAK: cross-tenant rows visible: {sorted(tenants)}"
