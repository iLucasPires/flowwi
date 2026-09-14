from importlib import import_module

from django.apps import AppConfig


class WorkplaceConfig(AppConfig):
    name = "apps.domains.workplace"
    verbose_name = "Workplace"

    def ready(self):
        import_module(".signals", package=self.name)
