from importlib import import_module

from django.apps import AppConfig


class UserConfig(AppConfig):
    name = "apps.domains.user"
    verbose_name = "User"

    def ready(self):
        import_module(".signals", package=self.name)
