from importlib import import_module

from django.apps import AppConfig


class DocumentConfig(AppConfig):
    name = "apps.domains.document"
    verbose_name = "Document"

    def ready(self):
        import_module(".signals", package=self.name)
