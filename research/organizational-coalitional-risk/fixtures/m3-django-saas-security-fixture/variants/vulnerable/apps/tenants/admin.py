from django.contrib import admin

from apps.tenants.models import Invitation, Membership, Tenant


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    autocomplete_fields = ["user"]


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "created_at"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MembershipInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "tenant", "role", "created_at"]
    list_filter = ["role", "tenant"]
    search_fields = ["user__email", "tenant__name"]
    autocomplete_fields = ["user", "tenant"]


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ["email", "tenant", "role", "status", "expires_at", "created_at"]
    list_filter = ["status", "role", "tenant"]
    search_fields = ["email", "tenant__name"]
