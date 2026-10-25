from __future__ import annotations

from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from apps.tenants.models import Invitation, Membership, Role, Tenant


class TenantSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = ["id", "name", "slug", "is_active", "role", "created_at"]
        read_only_fields = ["id", "slug", "is_active", "role", "created_at"]

    def get_role(self, obj) -> str | None:
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return None
        membership = next((m for m in obj.memberships.all() if m.user_id == request.user.id), None)
        return membership.role if membership else None


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ["id", "user", "role", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

    def validate_role(self, value: str) -> str:
        if value not in Role.values:
            raise serializers.ValidationError("Invalid role.")
        return value


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = [
            "id",
            "email",
            "role",
            "status",
            "expires_at",
            "accepted_at",
            "created_at",
        ]
        read_only_fields = ["id", "status", "expires_at", "accepted_at", "created_at"]

    def validate_role(self, value: str) -> str:
        # Inviting someone as an owner is disallowed; ownership is granted, not invited.
        if value == Role.OWNER:
            raise serializers.ValidationError("Cannot invite a user as owner.")
        return value


class InvitationAcceptSerializer(serializers.Serializer):
    token = serializers.CharField()
