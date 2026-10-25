"""Quarterly delivery report.

The tenant-facing HTTP endpoint binds the active tenant through middleware.
The nightly operations job has a separate fleet-scoped export and does not call
this builder.
"""
from __future__ import annotations

from django.db.models import Count

from apps.projects.models import Project


def build_delivery_report(start, end):
    """Per-project release counts for reporting period [start, end]."""
    rows = (
        Project.objects.filter(created_at__gte=start, created_at__lte=end)
        .values("tenant__slug", "status")
        .annotate(releases=Count("id"))
        .order_by("tenant__slug", "status")
    )
    return [
        {"tenant": r["tenant__slug"], "status": r["status"], "releases": r["releases"]}
        for r in rows
    ]
