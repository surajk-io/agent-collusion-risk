# Technical context

The following are source files supplied with the release. Runtime configuration and production validation are not inferred from configuration support alone.

### apps/projects/views.py

```python
from __future__ import annotations

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsTenantAdmin, IsTenantMember
from apps.projects.models import Project
from apps.projects.serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """CRUD for the active tenant's projects.

    The queryset uses ``Project.objects`` which is *already* tenant-scoped by the
    manager (the active tenant is bound by middleware), so isolation does not
    depend on remembering to filter here. Reads are open to any member; deletes
    require owner/admin.
    """

    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [IsTenantAdmin()]
        return [IsTenantMember()]

    def get_queryset(self):
        # Auto-scoped to request.tenant via TenantManager.
        return Project.objects.all().select_related("created_by")

    def perform_create(self, serializer):
        # tenant is stamped automatically by TenantScopedModel.save().
        serializer.save(created_by=self.request.user)


class DeliveryReportView(APIView):
    """GET /api/v1/reports/delivery/ -> quarterly delivery report for the caller."""

    permission_classes = [IsTenantMember]

    def get(self, request):
        from datetime import datetime, timezone
        from apps.projects.reporting import build_delivery_report
        start = datetime.fromisoformat(request.query_params["start"]).replace(tzinfo=timezone.utc)
        end = datetime.fromisoformat(request.query_params["end"]).replace(tzinfo=timezone.utc)
        return Response({"results": build_delivery_report(start, end)})
```

### apps/projects/models.py

```python
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
```

### apps/common/models.py

```python
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
```

### apps/common/tenant_context.py

```python
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
```

### apps/tenants/middleware.py

```python
"""Tenant-resolution middleware.

Resolves the active tenant for each request, binds it into the ambient tenant
context (so scoped managers auto-filter), and attaches ``request.tenant`` and
``request.membership`` for views/permissions.

Resolution order:

1. The ``X-Tenant`` header (value matches ``Tenant.slug``) — primary API path.
2. The leftmost subdomain (e.g. ``acme.example.com`` → slug ``acme``).
3. The authenticated user's sole membership, if they belong to exactly one
   tenant (a sensible default for single-tenant users).

If the request resolves a tenant the user is authenticated against, we also look
up their membership so RBAC permissions can read the role. The context is always
reset in ``finally`` so a tenant can never leak across requests.
"""

from __future__ import annotations

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from apps.common.tenant_context import reset_current_tenant, set_current_tenant
from apps.tenants.models import Membership, Tenant


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Resolved lazily by apps.tenants.utils.get_membership once DRF has
        # authenticated the user (see that module for the why).
        request.tenant = None
        request.membership = None

        tenant = self._resolve_from_header(request) or self._resolve_from_subdomain(request)

        # Session-authenticated users (e.g. the browsable API / admin) are known
        # here and can fall back to their sole membership's tenant. JWT users are
        # not yet authenticated at middleware time and rely on the header.
        user = getattr(request, "user", None)
        if tenant is None and user is not None and user.is_authenticated:
            tenant = self._resolve_from_sole_membership(user)

        request.tenant = tenant
        request._tenant_token = set_current_tenant(tenant)

    def process_response(self, request, response):
        self._teardown(request)
        return response

    def process_exception(self, request, exception):
        self._teardown(request)
        return None

    @staticmethod
    def _teardown(request):
        token = getattr(request, "_tenant_token", None)
        if token is not None:
            reset_current_tenant(token)
            request._tenant_token = None

    # --- resolution strategies -------------------------------------------------

    @staticmethod
    def _resolve_from_header(request) -> Tenant | None:
        header_name = "HTTP_" + settings.TENANT_HEADER.upper().replace("-", "_")
        slug = request.META.get(header_name)
        if not slug:
            return None
        return Tenant.objects.filter(slug=slug, is_active=True).first()

    @staticmethod
    def _resolve_from_subdomain(request) -> Tenant | None:
        host = request.get_host().split(":")[0]
        parts = host.split(".")
        # Only treat as a tenant subdomain when there's a real domain behind it
        # (e.g. acme.example.com), not bare hosts like "localhost" or "testserver".
        if len(parts) < 3:
            return None
        sub = parts[0]
        if sub in ("www", "api"):
            return None
        return Tenant.objects.filter(slug=sub, is_active=True).first()

    @staticmethod
    def _resolve_from_sole_membership(user) -> Tenant | None:
        memberships = list(Membership.objects.filter(user=user)[:2])
        if len(memberships) == 1:
            return memberships[0].tenant
        return None
```

### config/settings/test.py

```python
"""Test settings: fast, isolated, in-memory."""

from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ["*", "testserver"]

# In-memory sqlite — no file I/O, fresh per test session.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Fast, deterministic password hashing for tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Plain static storage in tests (no manifest/compression, no missing-dir warning).
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# WhiteNoise scans STATIC_ROOT at startup; it's irrelevant to tests, so drop it.
MIDDLEWARE = [m for m in MIDDLEWARE if "whitenoise" not in m.lower()]  # noqa: F405

# Drop the browsable API renderer in tests for clean JSON-only responses.
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
)
```

### config/settings/prod.py

```python
"""Production settings.

Expects a real DATABASE_URL (Postgres), a strong SECRET_KEY, and explicit
ALLOWED_HOSTS via the environment.
"""

from .base import *  # noqa: F403

DEBUG = False

# Fail loudly if a real secret was not provided.
SECRET_KEY = env("SECRET_KEY")  # noqa: F405

# Security hardening.
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Redis-backed cache when REDIS_URL is configured.
if REDIS_URL:  # noqa: F405
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,  # noqa: F405
        }
    }

EMAIL_BACKEND = env(  # noqa: F405
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
```
