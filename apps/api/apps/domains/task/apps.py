from django.apps import AppConfig


class TaskConfig(AppConfig):
    name = "apps.domains.task"
    label = "task"
    verbose_name = "Task"

    def ready(self):
        from . import signals  # noqa: F401
