from rest_framework.permissions import BasePermission


class StickyPermission(BasePermission):
    def has_permission(self, request, view):
        return True
