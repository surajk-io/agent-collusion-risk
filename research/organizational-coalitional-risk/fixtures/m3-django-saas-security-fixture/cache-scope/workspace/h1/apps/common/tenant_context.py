"""Ambient "current tenant" state for the active request.

The active tenant is stored in a :class:`contextvars.ContextVar`, which is safe
under both threaded (WSGI) and async (ASGI) servers — each request/task gets an
isolated copy, so one request can never leak its tenant into another.

Tenant-scoped managers read this value to auto-filter querysets, and writes use
it to stamp new rows. Code paths that legitimately span tenants (admin scripts,
data migrations, background jobs) opt out explicitly via :func:`unscoped`.
"""

from __future__ import annotations

import contextlib
from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterator

    from apps.tenants.models import Tenant

_current_tenant: ContextVar[Tenant | None] = ContextVar("current_tenant", default=None)


def get_current_tenant() -> Tenant | None:
    """Return the tenant bound to the current context, or ``None``."""
    return _current_tenant.get()


def set_current_tenant(tenant: Tenant | None):
    """Bind ``tenant`` to the current context. Returns the reset token."""
    return _current_tenant.set(tenant)


def reset_current_tenant(token) -> None:
    """Restore the previous tenant using a token from :func:`set_current_tenant`."""
    _current_tenant.reset(token)


@contextlib.contextmanager
def tenant_context(tenant: Tenant | None) -> Iterator[None]:
    """Temporarily bind ``tenant`` for the duration of the ``with`` block."""
    token = _current_tenant.set(tenant)
    try:
        yield
    finally:
        _current_tenant.reset(token)


@contextlib.contextmanager
def unscoped() -> Iterator[None]:
    """Run a block with no active tenant (cross-tenant access for trusted code)."""
    token = _current_tenant.set(None)
    try:
        yield
    finally:
        _current_tenant.reset(token)
