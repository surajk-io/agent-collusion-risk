from __future__ import annotations

from django.core.mail import send_mail
from django.db import IntegrityError
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import (
    IsTenantAdmin,
    IsTenantMember,
)
from apps.tenants.models import Invitation, Membership, Role, Tenant
from apps.tenants.serializers import (
    InvitationAcceptSerializer,
    InvitationSerializer,
    MembershipSerializer,
    TenantSerializer,
)


class TenantViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """The tenants the current user belongs to.

    Listing is scoped to the caller's memberships (not the active-tenant header)
    so a user can always discover their own workspaces. Mutating a tenant
    requires owner/admin in that tenant.
    """

    serializer_class = TenantSerializer

    def get_permissions(self):
        if self.action in ("update", "partial_update"):
            return [IsTenantAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return (
            Tenant.objects.filter(memberships__user=self.request.user)
            .prefetch_related("memberships")
            .distinct()
        )


class MembershipViewSet(viewsets.ModelViewSet):
    """Members of the active tenant. Admin-only for writes."""

    serializer_class = MembershipSerializer

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [IsTenantMember()]
        return [IsTenantAdmin()]

    def get_queryset(self):
        # request.tenant is set by TenantMiddleware.
        return Membership.objects.filter(tenant=self.request.tenant).select_related("user")

    def perform_destroy(self, instance):
        if instance.role == Role.OWNER:
            raise ValidationError("Cannot remove the owner. Transfer ownership first.")
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.role == Role.OWNER and request.data.get("role") not in (None, Role.OWNER):
            raise ValidationError("Cannot demote the owner.")
        return super().update(request, *args, **kwargs)


class InvitationViewSet(viewsets.ModelViewSet):
    """Invitations for the active tenant, plus a public accept action."""

    serializer_class = InvitationSerializer

    def get_permissions(self):
        if self.action == "accept":
            return [IsAuthenticated()]
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [IsTenantMember()]
        return [IsTenantAdmin()]

    def get_queryset(self):
        # `accept` is keyed by token and must look across tenants for the caller.
        if self.action == "accept":
            return Invitation.objects.all()
        return Invitation.objects.filter(tenant=self.request.tenant).select_related("tenant")

    def perform_create(self, serializer):
        tenant = self.request.tenant
        email = serializer.validated_data["email"].lower()
        if Membership.objects.filter(tenant=tenant, user__email=email).exists():
            raise ValidationError("That user is already a member of this tenant.")
        try:
            invitation = serializer.save(
                tenant=tenant,
                email=email,
                invited_by=self.request.user,
            )
        except IntegrityError:
            raise ValidationError("A pending invitation for this email already exists.")
        self._send_invitation_email(invitation)

    @staticmethod
    def _send_invitation_email(invitation: Invitation) -> None:
        send_mail(
            subject=f"You've been invited to {invitation.tenant.name}",
            message=(
                f"You have been invited to join {invitation.tenant.name} "
                f"as {invitation.role}. Accept token: {invitation.token}"
            ),
            from_email=None,
            recipient_list=[invitation.email],
            fail_silently=True,
        )

    @action(detail=False, methods=["post"], url_path="accept")
    def accept(self, request):
        """Accept an invitation by token; creates the caller's membership.

        Does not require the X-Tenant header — the token identifies the tenant.
        """
        serializer = InvitationAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]

        invitation = Invitation.objects.filter(token=token).select_related("tenant").first()
        if invitation is None:
            raise ValidationError("Invalid invitation token.")
        if invitation.email.lower() != request.user.email.lower():
            raise PermissionDenied("This invitation was issued to a different email address.")
        if not invitation.is_pending:
            raise ValidationError("Invitation is no longer valid.")

        membership = invitation.accept(request.user)
        return Response(
            {
                "detail": "Invitation accepted.",
                "tenant": TenantSerializer(invitation.tenant, context={"request": request}).data,
                "role": membership.role,
            },
            status=status.HTTP_200_OK,
        )
