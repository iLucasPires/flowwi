from django.db import models
from django_stubs_ext.db.models import TypedModelMeta


class CreatedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(TypedModelMeta):
        abstract = True


class UpdatedModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TypedModelMeta):
        abstract = True


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta(TypedModelMeta):
        abstract = True


class TimeStampedModel(CreatedModel, UpdatedModel):
    class Meta(TypedModelMeta):
        abstract = True


class TimeStampedSoftDeleteModel(TimeStampedModel, SoftDeleteModel):
    class Meta(TypedModelMeta):
        abstract = True
