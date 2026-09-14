import os
import uuid
from datetime import date

from django.utils.deconstruct import deconstructible


def upload_to_uuid(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    today = date.today()

    return f"uploads/{today.year}/{today.month:02d}/{today.day:02d}/{uuid.uuid4().hex}{ext}"


@deconstructible
class upload_to_path:
    """Deconstructible callable for Django FileField upload_to."""

    def __init__(self, *path_parts):
        self.path_parts = path_parts

    def __call__(self, instance, filename):
        ext = os.path.splitext(filename)[1].lower()
        today = date.today()
        prefix = "/".join(self.path_parts)

        return f"{prefix}/{today.year}/{today.month:02d}/{uuid.uuid4().hex}{ext}"
