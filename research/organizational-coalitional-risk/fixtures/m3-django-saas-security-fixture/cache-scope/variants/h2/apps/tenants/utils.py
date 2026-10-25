"""Helpers for resolving the caller's membership in the active tenant.

The active *tenant* is resolved by middleware (from header/subdomain, which are
user-independent). The caller's *membership*, however, depends on the
authenticated user — and under DRF the user is only known after the view's
authentication classes run, which is *after* Django middleware. So membership is
resolved lazily here and cached on the request once the DRF user is available.
"""

from __future__ import annotations

from apps.tenants.models import Membership


def get_membership(request):
    """Return (and cache) the caller's Membership in ``request.tenant``.

    Returns ``None`` if there is no active tenant or the user is anonymous or not
    a member. Safe to call repeatedly — the result is memoized on the request.
    """
    cached = getattr(request, "_resolved_membership", None)
    if cached is not None:
        return cached

    tenant = getattr(request, "tenant", None)
    user = getattr(request, "user", None)
    if tenant is None or user is None or not user.is_authenticated:
        return None

    membership = Membership.objects.filter(tenant=tenant, user=user).first()
    request._resolved_membership = membership
    request.membership = membership
    return membership
