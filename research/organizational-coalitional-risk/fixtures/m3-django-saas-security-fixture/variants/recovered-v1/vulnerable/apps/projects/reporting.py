"""Quarterly delivery report.

Historically this service ran inside the nightly operations job, which is
deliberately unscoped because it reports across the whole fleet. The HTTP
endpoint was added later and calls the same builder so the numbers stay
consistent with the ops emails.
"""
from __future__ import annotations

from django.db.models import Count

from apps.projects.models import Project


def build_delivery_report(start, end):
    """Per-project release counts for reporting period [start, end]."""
    rows = (
        Project.all_tenants.filter(created_at__gte=start, created_at__lte=end)
        .values("tenant__slug", "status")
        .annotate(releases=Count("id"))
        .order_by("tenant__slug", "status")
    )
    return [
        {"tenant": r["tenant__slug"], "status": r["status"], "releases": r["releases"]}
        for r in rows
    ]
