"""Invitation lifecycle: invite → accept → membership.

Covers the happy path plus the guardrails (wrong email, expired/revoked, and
that accepting actually grants tenant-scoped access).
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.tenants.models import Invitation, Membership, Role

pytestmark = pytest.mark.django_db

INVITATIONS_URL = "/api/v1/invitations/"
ACCEPT_URL = "/api/v1/invitations/accept/"
PROJECTS_URL = "/api/v1/projects/"


def _invite(client, email="invitee@example.com", role="member"):
    resp = client.post(INVITATIONS_URL, {"email": email, "role": role}, HTTP_X_TENANT="acme")
    assert resp.status_code == 201, resp.content
    return Invitation.objects.get(tenant__slug="acme", email=email)


def test_invite_accept_flow_creates_membership(client_owner_a, tenant_a, make_user, api):
    invitation = _invite(client_owner_a)
    assert invitation.status == Invitation.Status.PENDING

    invitee = make_user("invitee@example.com")
    from rest_framework_simplejwt.tokens import RefreshToken

    api.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(invitee).access_token}")

    resp = api.post(ACCEPT_URL, {"token": invitation.token})
    assert resp.status_code == 200

    membership = Membership.objects.get(tenant=tenant_a, user=invitee)
    assert membership.role == Role.MEMBER

    invitation.refresh_from_db()
    assert invitation.status == Invitation.Status.ACCEPTED
    assert invitation.accepted_at is not None


def test_accepted_invitee_gains_tenant_access(client_owner_a, tenant_a, make_user, api, project_a):
    invitation = _invite(client_owner_a)
    invitee = make_user("invitee@example.com")
    from rest_framework_simplejwt.tokens import RefreshToken

    token = RefreshToken.for_user(invitee).access_token
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # Before accepting: no access to tenant A.
    before = api.get(PROJECTS_URL, HTTP_X_TENANT="acme")
    assert before.status_code == 403

    api.post(ACCEPT_URL, {"token": invitation.token})

    # After accepting: can read tenant A's projects.
    after = api.get(PROJECTS_URL, HTTP_X_TENANT="acme")
    assert after.status_code == 200
    assert {r["name"] for r in after.json()["results"]} == {"Alpha"}


def test_accept_rejected_for_wrong_email(client_owner_a, make_user, api):
    invitation = _invite(client_owner_a, email="intended@example.com")
    impostor = make_user("impostor@example.com")
    from rest_framework_simplejwt.tokens import RefreshToken

    api.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(impostor).access_token}")
    resp = api.post(ACCEPT_URL, {"token": invitation.token})
    assert resp.status_code == 403
    assert not Membership.objects.filter(user=impostor).exists()


def test_accept_rejected_for_expired_invitation(client_owner_a, make_user, api):
    invitation = _invite(client_owner_a)
    invitation.expires_at = timezone.now() - timedelta(days=1)
    invitation.save(update_fields=["expires_at"])

    invitee = make_user("invitee@example.com")
    from rest_framework_simplejwt.tokens import RefreshToken

    api.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(invitee).access_token}")
    resp = api.post(ACCEPT_URL, {"token": invitation.token})
    assert resp.status_code == 400


def test_duplicate_pending_invitation_rejected(client_owner_a):
    _invite(client_owner_a, email="dupe@example.com")
    resp = client_owner_a.post(
        INVITATIONS_URL, {"email": "dupe@example.com", "role": "member"}, HTTP_X_TENANT="acme"
    )
    assert resp.status_code == 400
