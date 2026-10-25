"""Tenant-aware RBAC permissions for DRF views.

The active *tenant* is bound by :class:`apps.tenants.middleware.TenantMiddleware`
as ``request.tenant``. The caller's *membership* (and therefore role) is resolved
lazily via :func:`apps.tenants.utils.get_membership`, because under DRF the
authenticated user is only known after the view runs its authentication classes —
which is after Django middleware. These permissions gate actions by that role.
"""

from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.tenants.models import Role
from apps.tenants.utils import get_membership


class HasActiveTenant(BasePermission):
    """Require that a tenant was resolved for this request."""

    message = "No active tenant. Provide the X-Tenant header or use a tenant subdomain."

    def has_permission(self, request, view) -> bool:
        return getattr(request, "tenant", None) is not None


class IsTenantMember(HasActiveTenant):
    """Require an authenticated user with a membership in the active tenant."""

    message = "You are not a member of this tenant."

    def has_permission(self, request, view) -> bool:
        if not super().has_permission(request, view):
            return False
        return get_membership(request) is not None


class IsTenantAdmin(IsTenantMember):
    """Owner/admin for writes; any member may read (safe methods)."""

    message = "This action requires an owner or admin role."

    def has_permission(self, request, view) -> bool:
        if not super().has_permission(request, view):
            return False
        if request.method in SAFE_METHODS:
            return True
        return get_membership(request).role in (Role.OWNER, Role.ADMIN)


class IsTenantOwner(IsTenantMember):
    """Owner for writes; any member may read."""

    message = "This action requires the owner role."

    def has_permission(self, request, view) -> bool:
        if not super().has_permission(request, view):
            return False
        if request.method in SAFE_METHODS:
            return True
        return get_membership(request).role == Role.OWNER
