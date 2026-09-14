from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction


class ServiceBase:
    """
    Base service with queryset access and essential helpers.

    For simple CRUD, use the queryset/model directly in viewsets.
    Subclass this only when you have real business logic.
    """

    model: type[models.Model]

    def __init__(self, model: type[models.Model]):
        self.model = model

    def get_queryset(self) -> models.QuerySet:
        """Override to add select_related, prefetch, or scope filtering."""
        return self.model.objects.all()

    def get_or_none(self, **kwargs) -> models.Model | None:
        try:
            return self.get_queryset().get(**kwargs)
        except ObjectDoesNotExist:
            return None

    def filter(self, **kwargs) -> models.QuerySet:
        return self.get_queryset().filter(**kwargs)

    def exists(self, **kwargs) -> bool:
        return self.filter(**kwargs).exists()

    @transaction.atomic
    def create(self, data: dict[str, Any]) -> models.Model:
        return self.model.objects.create(**data)

    @transaction.atomic
    def bulk_create(self, instances: list[models.Model]) -> list[models.Model]:
        return self.model.objects.bulk_create(instances)

    @transaction.atomic
    def get_or_create(self, **kwargs) -> tuple[models.Model, bool]:
        return self.model.objects.get_or_create(**kwargs)
