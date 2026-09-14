from django.db.models import QuerySet
from guardian.shortcuts import get_objects_for_user

from ..permissions import DocumentAccess


class DocumentSelector:
    @staticmethod
    def viewable_for(workplace, user) -> QuerySet:
        """
        Every document in `workplace` that `user` may view — unfiltered for workplace
        admins. Scopes DocumentVersion/Comment/Feedback querysets too, since their own
        viewsets otherwise only check workplace membership, not per-document sharing —
        without this, a private document's content/comments would leak through those
        endpoints even though the document itself is hidden.
        """
        from ..models import Document

        base = Document.objects.filter(workplace=workplace)

        if DocumentAccess().is_workplace_admin(workplace, user):
            return base

        return get_objects_for_user(user, "document.view_document", klass=base, accept_global_perms=False)
