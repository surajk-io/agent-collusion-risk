from __future__ import annotations

from rest_framework import viewsets

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
