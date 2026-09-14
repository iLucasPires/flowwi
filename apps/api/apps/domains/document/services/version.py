from django.db import models, transaction

from lib.bases import ServiceBase

from ..models import DocumentVersion


class DocumentVersionService(ServiceBase):
    def __init__(self):
        super().__init__(model=DocumentVersion)

    @transaction.atomic
    def add_version(self, document_id: int, *, content: str | None = None) -> DocumentVersion:
        next_v = (
            DocumentVersion.objects.filter(document_id=document_id).aggregate(
                max_v=models.Max("number"),
            )["max_v"]
            or 0
        ) + 1

        return DocumentVersion.objects.create(
            document_id=document_id,
            number=next_v,
            content=content if content is not None else "",
        )

    @transaction.atomic
    def new_revision(self, version_id: int) -> DocumentVersion:
        """Branch a new draft version off the given version's content."""
        source = DocumentVersion.objects.get(pk=version_id)
        return self.add_version(source.document_id, content=source.content)
