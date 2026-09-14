from django.apps import AppConfig


class InboxConfig(AppConfig):
    name = "apps.domains.inbox"
    verbose_name = "Inbox"

    def ready(self):
        import apps.domains.inbox.signals  # noqa: F401
