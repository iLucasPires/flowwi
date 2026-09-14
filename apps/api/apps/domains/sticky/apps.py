from django.apps import AppConfig


class StickyConfig(AppConfig):
    name = "apps.domains.sticky"

    def ready(self):
        from . import signals  # noqa: F401
