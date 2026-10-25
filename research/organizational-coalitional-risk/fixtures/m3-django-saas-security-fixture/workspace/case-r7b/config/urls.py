"""Root URL configuration."""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


def healthcheck(_request):
    return JsonResponse({"status": "ok"})


api_v1 = [
    path("auth/register/", include("apps.accounts.urls")),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include("apps.tenants.urls")),
    path("", include("apps.projects.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthcheck, name="healthz"),
    path("api/v1/", include((api_v1, "api"), namespace="v1")),
    # DRF browsable-API login/logout.
    path("api-auth/", include("rest_framework.urls")),
]
