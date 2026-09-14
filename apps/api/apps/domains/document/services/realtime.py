from lib.utils import channel_name as build_channel_name

from ..permissions import DocumentAccess
from .lock import DocumentLock, DocumentLockService


class DocumentRealtimeService:
    """
    Business logic behind the document realtime protocol (subscribe/lock/heartbeat) —
    consumed by `DocumentRealtimeHandler`, which only owns the WebSocket-facing
    protocol (parsing messages, sending/broadcasting frames, this connection's own
    bookkeeping). The actual rules — who may subscribe, who may hold the lock — live
    here, next to the rest of the document domain.
    """

    def __init__(self):
        self.access = DocumentAccess()
        self.lock_service = DocumentLockService()

    def group_name(self, document_id) -> str:
        return build_channel_name("document", document_id)

    def can_subscribe(self, document_id, user) -> bool:
        document = self._get_document(document_id)
        return self.access.can_view(user, document)

    def try_acquire_lock(self, document_id, user) -> DocumentLock | None:
        """`None` means denied — either no edit permission, or someone else holds it."""
        document = self._get_document(document_id)

        if not self.access.can_edit(user, document):
            return None

        return self.lock_service.try_acquire(document_id, user.id, user.username)

    def get_lock(self, document_id) -> DocumentLock | None:
        return self.lock_service.get(document_id)

    def refresh_lock(self, document_id, user_id: int) -> bool:
        return self.lock_service.refresh(document_id, user_id)

    def release_lock(self, document_id, user_id: int) -> bool:
        return self.lock_service.release(document_id, user_id)

    def _get_document(self, document_id):
        from ..models import Document

        return Document.objects.filter(pk=document_id).select_related("workplace").first()
