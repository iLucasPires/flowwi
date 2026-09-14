from django.db import models, transaction

from apps.domains.media.models import MediaVersion, MediaVersionType
from lib.bases import ServiceBase


class MediaVersionService(ServiceBase):
    def __init__(self):
        super().__init__(model=MediaVersion)

    @transaction.atomic
    def add_version(
        self,
        media_id: int,
        *,
        drive_file_id: str,
        drive_url: str,
        file_name: str,
        mime_type: str,
        type: int | None = None,
    ):
        next_v = (
            MediaVersion.objects.filter(media_id=media_id).aggregate(
                max_v=models.Max("number"),
            )["max_v"]
            or 0
        ) + 1

        return MediaVersion.objects.create(
            media_id=media_id,
            number=next_v,
            drive_file_id=drive_file_id,
            drive_url=drive_url,
            file_name=file_name,
            mime_type=mime_type,
            type=type or MediaVersionType.IMAGE,
        )
