from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models.member import WorkplaceMemberRole


class IsDesignerOrReadOnly(BasePermission):
    """Allow designers full access, others read-only."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user and request.user.is_authenticated


class IsWorkplaceAdminToManageMembers(BasePermission):
    """Editing another member's role/status or removing them requires owner/manager.

    A manager can manage other managers and designers, but never an owner —
    only the owner themselves can edit, approve, or remove an owner membership.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or view.action == "create":
            return True

        workplace = view.get_workplace()
        return bool(workplace and workplace.is_admin(request.user))

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if obj.role != WorkplaceMemberRole.OWNER:
            return True

        return obj.workplace.is_owner(request.user)
