from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

RETENTION_DAYS = 5


class Command(BaseCommand):
    help = "Permanently deletes tasks and stickies that were soft-deleted more than N days ago."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=RETENTION_DAYS,
            help=f"Retention period in days before permanent deletion (default: {RETENTION_DAYS}).",
        )

    def handle(self, *args, **options):
        from apps.domains.sticky.models import Sticky
        from apps.domains.sticky.services import StickyService
        from apps.domains.task.models import Task
        from apps.domains.task.services import TaskService

        cutoff = timezone.now() - timedelta(days=options["days"])
        purged = 0

        for task in Task.objects.filter(deleted_at__isnull=False, deleted_at__lt=cutoff):
            TaskService().purge(task)
            purged += 1

        for sticky in Sticky.objects.filter(deleted_at__isnull=False, deleted_at__lt=cutoff):
            StickyService().purge(sticky)
            purged += 1

        self.stdout.write(self.style.SUCCESS(f"Purged {purged} item(s)."))
