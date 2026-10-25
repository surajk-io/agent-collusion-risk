from django.contrib import admin

from apps.projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # Uses the unscoped manager so admins can see across all tenants.
    list_display = ["name", "tenant", "status", "created_by", "created_at"]
    list_filter = ["status", "tenant"]
    search_fields = ["name", "tenant__name"]
    autocomplete_fields = ["tenant", "created_by"]

    def get_queryset(self, request):
        return Project.all_tenants.all()
