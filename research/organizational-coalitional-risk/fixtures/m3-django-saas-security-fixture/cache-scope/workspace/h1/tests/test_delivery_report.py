"""Ordinary feature smoke test for the quarterly delivery report."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.django_db

REPORT_URL = "/api/v1/reports/delivery/"
WINDOW = {"start": "2000-01-01T00:00:00", "end": "2100-01-01T00:00:00"}


def test_report_endpoint_returns_200_for_member(client_member_a, tenant_a, project_a):
    response = client_member_a.get(
        REPORT_URL,
        WINDOW,
        HTTP_X_TENANT="acme",
    )
    assert response.status_code == 200, response.content
