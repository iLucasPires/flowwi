import uuid

from django.db import models
from django_stubs_ext.db.models import TypedModelMeta


class UUIDModel(models.Model):
    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
    )

    class Meta(TypedModelMeta):
        abstract = True
