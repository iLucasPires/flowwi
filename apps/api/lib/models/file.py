from django.db import models
from django_stubs_ext.db.models import TypedModelMeta


class FileCleanupModel(models.Model):
    file_fields: tuple[str, ...] = ()

    class Meta(TypedModelMeta):
        abstract = True

    def save(self, *args, **kwargs):
        self._delete_replaced_files()
        super().save(*args, **kwargs)

    def _delete_replaced_files(self) -> None:
        """Remove files that were replaced before saving."""
        if not self.pk or not self.file_fields:
            return

        try:
            old_instance = self.__class__.objects.get(pk=self.pk)

        except self.__class__.DoesNotExist:
            return

        for field_name in self.file_fields:
            self._delete_old_file(old_instance, field_name)

    def _delete_old_file(self, old_instance: models.Model, field_name: str) -> None:
        old_file = getattr(old_instance, field_name, None)
        new_file = getattr(self, field_name, None)

        if old_file and old_file != new_file:
            old_file.delete(save=False)
