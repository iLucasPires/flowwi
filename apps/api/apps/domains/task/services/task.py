from django.utils import timezone

from lib.bases import ServiceBase

from ..models import Task


class TaskService(ServiceBase):
    def __init__(self):
        super().__init__(Task)

    def trash(self, task: Task, *, deleted_by=None) -> Task:
        task.deleted_at = timezone.now()
        task.save(update_fields=["deleted_at", "updated_at"])
        return task

    def restore(self, task: Task) -> Task:
        task.deleted_at = None
        task.save(update_fields=["deleted_at", "updated_at"])
        return task

    def purge(self, task: Task) -> None:
        task.delete()
