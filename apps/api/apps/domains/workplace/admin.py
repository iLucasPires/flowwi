from django.contrib import admin

from .models import Workplace, WorkplaceMember, WorkplaceMemberRole


@admin.register(Workplace)
class WorkplaceAdmin(admin.ModelAdmin):
    list_display = (
        "public_id",
        "name",
        "slug",
        "photo",
        "is_active",
        "invite_key",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "slug",
    )
    actions = (
        "make_active",
        "make_inactive",
    )

    @admin.action(description="Make active")
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Make inactive")
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Workplaces marked as inactive")
        return queryset


@admin.register(WorkplaceMember)
class WorkplaceMemberAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "workplace",
        "role",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "role",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "user__username",
        "user__email",
    )
    actions = ("make_owner",)

    @admin.action(description="Make owner")
    def make_owner(self, request, queryset):
        queryset.update(role=WorkplaceMemberRole.OWNER)
        self.message_user(request, "Workplace members marked as owner")
        return queryset
