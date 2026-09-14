"""
Object-level access control for `Document` and everything that hangs off one (its
versions, via `DocumentRelatedObjectPermission`) — resolved with django-guardian
(`view_document`/`change_document`, kept in sync by `apps.document.signals`),
with workplace admins (owner/manager) always overriding it.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class DocumentAccess:
    """
    The actual access rules, kept separate from any `BasePermission` subclass so
    they're usable everywhere a `request`/`view` pair doesn't exist — the WebSocket
    protocol (`DocumentRealtimeService`) and the `perform_create` hooks on
    comment/feedback/version viewsets that need a plain yes/no before a related object
    even has an object-level permission check to run against.
    """

    def is_workplace_admin(self, workplace, user) -> bool:
        """Owners and managers see and edit every document, overriding its own sharing."""
        return bool(workplace) and (workplace.is_owner(user) or workplace.is_manager(user))

    def can_view(self, user, document) -> bool:
        if document is None:
            return False
        if self.is_workplace_admin(document.workplace, user):
            return True
        return user.has_perm("document.view_document", document)

    def can_edit(self, user, document) -> bool:
        if document is None:
            return False
        if self.is_workplace_admin(document.workplace, user):
            return True
        return user.has_perm("document.change_document", document)


class BaseDocumentPermission(BasePermission):
    """
    Shared object-permission shape: resolve the `Document` behind `obj` (subclasses
    say how), let workplace admins through unconditionally, otherwise defer to
    `has_document_permission`. `get_queryset` on the viewset already excludes documents
    the user can't view at all (so those 404), so this only needs to gate what happens
    once an object *is* reachable — mainly write access.
    """

    access = DocumentAccess()

    def get_document(self, obj):
        raise NotImplementedError

    def has_document_permission(self, request, document) -> bool:
        raise NotImplementedError

    def has_object_permission(self, request, view, obj) -> bool:
        document = self.get_document(obj)

        if self.access.is_workplace_admin(document.workplace, request.user):
            return True

        return self.has_document_permission(request, document)


class DocumentObjectPermission(BaseDocumentPermission):
    """
    1. Workplace admins (owner/manager) — always full access, no exceptions.
    2. Everyone else — `view_document`/`change_document`, resolved by django-guardian
       from `Document.visibility`/`allow_member_edit`.
    3. Deleting is reserved for the author and workplace admins, even if a member was
       granted edit access — editing content and deleting the document are not the
       same permission in any market-standard sharing model.
    """

    def get_document(self, obj):
        return obj

    def has_document_permission(self, request, document) -> bool:
        if request.method == "DELETE":
            return document.author_id == request.user.id
        if request.method in SAFE_METHODS:
            return self.access.can_view(request.user, document)
        return self.access.can_edit(request.user, document)


class DocumentRelatedObjectPermission(BaseDocumentPermission):
    """
    Same resolution as `DocumentObjectPermission`, for objects that hang off a Document
    (versions) instead of being one — the guardian grant lives on `obj.document`, not
    on `obj` itself.
    """

    document_field = "document"

    def get_document(self, obj):
        return getattr(obj, self.document_field, None)

    def has_document_permission(self, request, document) -> bool:
        if request.method in SAFE_METHODS:
            return self.access.can_view(request.user, document)
        return self.access.can_edit(request.user, document)
