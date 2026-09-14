from django.core.exceptions import ValidationError
from django.db import transaction

from lib.bases import ServiceBase

from ..models import MediaComment


class MediaCommentService(ServiceBase):
    def __init__(self):
        super().__init__(model=MediaComment)

    @transaction.atomic
    def add_comment(
        self,
        media_id: int,
        author_id: int | None = None,
        version_id: int | None = None,
        content: str = "",
        guest_name: str = "",
    ):
        if not content:
            raise ValidationError("Content cannot be empty")

        if author_id is None and not guest_name:
            raise ValidationError("A comment needs either an author or a guest name.")

        return MediaComment.objects.create(
            media_id=media_id,
            version_id=version_id,
            author_id=author_id,
            content=content,
            guest_name=guest_name,
        )
