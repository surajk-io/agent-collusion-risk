"""Tenancy and RBAC domain models.

- :class:`Tenant` is the organization / workspace boundary.
- :class:`Membership` joins a user to a tenant with a :class:`Role`; this is the
  RBAC table — a user can belong to many tenants with a different role in each.
- :class:`Invitation` models the invite-by-email → accept flow.
"""

from __future__ import annotations

import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel


class Role(models.TextChoices):
    OWNER = "owner", "Owner"
    ADMIN = "admin", "Admin"
    MEMBER = "member", "Member"


class Tenant(TimeStampedModel):
    """An organization. The unit of data isolation."""

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=63, unique=True, help_text="Used in subdomains and the X-Tenant header.")
    is_active = models.BooleanField(default=True)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Membership",
        related_name="tenants",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Membership(TimeStampedModel):
    """A user's role within a tenant. The RBAC join table."""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.MEMBER)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["tenant", "user"], name="uniq_membership_per_tenant"),
        ]
        ordering = ["tenant", "role"]

    def __str__(self) -> str:
        return f"{self.user} @ {self.tenant} ({self.role})"

    @property
    def is_admin(self) -> bool:
        return self.role in (Role.OWNER, Role.ADMIN)

    @property
    def is_owner(self) -> bool:
        return self.role == Role.OWNER


def _default_token() -> str:
    return secrets.token_urlsafe(32)


def _default_expiry():
    return timezone.now() + timedelta(days=7)


class Invitation(TimeStampedModel):
    """A pending invite for an email address to join a tenant with a role."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REVOKED = "revoked", "Revoked"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="invitations")
    email = models.EmailField()
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.MEMBER)
    token = models.CharField(max_length=64, unique=True, default=_default_token, editable=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_invitations",
    )
    expires_at = models.DateTimeField(default=_default_expiry)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # At most one *pending* invite per (tenant, email).
            models.UniqueConstraint(
                fields=["tenant", "email"],
                condition=models.Q(status="pending"),
                name="uniq_pending_invitation_per_email",
            ),
        ]

    def __str__(self) -> str:
        return f"Invite {self.email} → {self.tenant} ({self.status})"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_pending(self) -> bool:
        return self.status == self.Status.PENDING and not self.is_expired

    def accept(self, user) -> Membership:
        """Accept this invite for ``user``, creating/raising their membership.

        Idempotent-ish: re-accepting an already-accepted invite returns the
        existing membership. Raises ``ValueError`` if the invite is not pending.
        """
        if not self.is_pending:
            raise ValueError("Invitation is not pending or has expired.")

        membership, _created = Membership.objects.get_or_create(
            tenant=self.tenant,
            user=user,
            defaults={"role": self.role},
        )
        self.status = self.Status.ACCEPTED
        self.accepted_at = timezone.now()
        self.save(update_fields=["status", "accepted_at", "updated_at"])
        return membership
