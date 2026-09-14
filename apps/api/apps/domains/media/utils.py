import os

from lib.constants import (
    DOCUMENT_EXTENSIONS,
    IMAGE_EXTENSIONS,
    TEXT_EXTENSIONS,
    VIDEO_EXTENSIONS,
)

from .models import MediaVersionType


def get_media_version_type_by_file_name(file_name: str) -> MediaVersionType:
    ext = os.path.splitext(file_name)[1].lower()

    if ext in IMAGE_EXTENSIONS:
        return MediaVersionType.IMAGE

    if ext in VIDEO_EXTENSIONS:
        return MediaVersionType.VIDEO

    if ext in TEXT_EXTENSIONS:
        return MediaVersionType.TEXT

    if ext in DOCUMENT_EXTENSIONS:
        return MediaVersionType.DOCUMENT

    return MediaVersionType.FILE
