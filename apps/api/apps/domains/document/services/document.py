from django.utils import timezone

from lib.bases import ServiceBase

from ..models import Document


class DocumentService(ServiceBase):
    def __init__(self):
        super().__init__(model=Document)

    def trash(self, document: Document, *, deleted_by=None) -> Document:
        document.deleted_at = timezone.now()
        document.deleted_by = deleted_by
        document.save(update_fields=["deleted_at", "deleted_by", "updated_at"])
        return document

    def restore(self, document: Document) -> Document:
        document.deleted_at = None
        document.deleted_by = None
        document.save(update_fields=["deleted_at", "deleted_by", "updated_at"])
        return document
