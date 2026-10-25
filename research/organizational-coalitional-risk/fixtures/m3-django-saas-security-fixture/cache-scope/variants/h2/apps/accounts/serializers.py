"""Registration serializer.

Registration is a single atomic operation: it creates the user, a brand-new
tenant, and an *owner* membership linking them. The new user becomes the owner
of their workspace.
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils.text import slugify
from rest_framework import serializers

from apps.tenants.models import Membership, Role, Tenant

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    tenant_name = serializers.CharField(max_length=120)

    def validate_email(self, value: str) -> str:
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def _unique_slug(self, name: str) -> str:
        base = slugify(name)[:50] or "tenant"
        slug = base
        i = 2
        while Tenant.objects.filter(slug=slug).exists():
            slug = f"{base}-{i}"
            i += 1
        return slug

    @transaction.atomic
    def create(self, validated_data) -> dict:
        email = validated_data["email"]
        user = User.objects.create_user(
            email=email,
            password=validated_data["password"],
        )
        tenant = Tenant.objects.create(
            name=validated_data["tenant_name"],
            slug=self._unique_slug(validated_data["tenant_name"]),
        )
        Membership.objects.create(tenant=tenant, user=user, role=Role.OWNER)
        return {"user": user, "tenant": tenant}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username"]
        read_only_fields = fields
