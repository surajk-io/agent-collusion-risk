from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.serializers import RegisterSerializer, UserSerializer
from apps.tenants.serializers import TenantSerializer


class RegisterView(APIView):
    """Register a user, create their tenant, and return JWT credentials.

    Open to anonymous callers (you cannot have a tenant before you register).
    """

    permission_classes = [AllowAny]
    authentication_classes: list = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        user, tenant = result["user"], result["tenant"]

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "tenant": TenantSerializer(tenant, context={"request": request}).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )
