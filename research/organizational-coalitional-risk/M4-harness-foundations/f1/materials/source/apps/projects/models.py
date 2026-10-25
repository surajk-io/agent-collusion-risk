"""Sample tenant-scoped resource.

``Project`` inherits :class:`TenantScopedModel`, so it gets a ``tenant`` FK, an
auto-filtering default manager, and tenant-stamping on save — without any
per-model boilerplate. This is the template every business resource follows.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import TenantScopedModel


class Project(TenantScopedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_projects",
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "name"], name="uniq_project_name_per_tenant"),
        ]

    def __str__(self) -> str:
        return self.name
