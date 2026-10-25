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
