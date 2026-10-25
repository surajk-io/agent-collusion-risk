"""Reusable model building blocks: timestamps and tenant scoping.

Row-level tenancy is enforced here. Every tenant-owned table carries a
``tenant`` foreign key, and :class:`TenantScopedModel` swaps in a manager that
*automatically* filters by the active tenant (see ``tenant_context``). The aim
is that application code can never accidentally read or write across tenants —
the default ``.objects`` is already scoped, and crossing tenants requires an
explicit, auditable opt-out.
"""

from __future__ import annotations

from django.core.exceptions import ImproperlyConfigured
from django.db import models

from apps.common.tenant_context import get_current_tenant


class TimeStampedModel(models.Model):
    """Adds self-managed ``created_at`` / ``updated_at`` columns."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantQuerySet(models.QuerySet):
    """A queryset that knows how to restrict itself to a single tenant."""

    def for_tenant(self, tenant) -> TenantQuerySet:
        return self.filter(tenant=tenant)


class TenantManager(models.Manager.from_queryset(TenantQuerySet)):
    """Default manager that auto-filters to the active tenant.

    When a tenant is bound to the current context, ``get_queryset`` returns only
    that tenant's rows. When *no* tenant is bound, it returns an **empty**
    queryset by default — failing closed rather than leaking every tenant's data
    on an unscoped code path. Trusted cross-tenant access goes through
    :attr:`Model.all_tenants` (the unscoped manager) or the ``unscoped()``
    context manager.
    """

    def get_queryset(self) -> TenantQuerySet:
        qs = super().get_queryset()
        tenant = get_current_tenant()
        if tenant is None:
            return qs.none()
        return qs.filter(tenant=tenant)


class TenantScopedModel(TimeStampedModel):
    """Abstract base for any model that belongs to exactly one tenant."""

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        db_index=True,
    )

    # Default manager: scoped to the active tenant. Used by all "normal" code.
    objects = TenantManager()
    # Escape hatch: unscoped access for admin, migrations, and background jobs.
    all_tenants = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Stamp the active tenant on create if one wasn't set explicitly."""
        if self.tenant_id is None:
            tenant = get_current_tenant()
            if tenant is None:
                raise ImproperlyConfigured(
                    f"Cannot save {type(self).__name__} without a tenant: no "
                    "tenant is bound to the current context and none was set "
                    "explicitly."
                )
            self.tenant = tenant
        super().save(*args, **kwargs)
