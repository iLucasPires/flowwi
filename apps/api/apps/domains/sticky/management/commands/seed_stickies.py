import random

from django.core.management.base import BaseCommand, CommandError

from apps.domains.sticky.factories import StickyFactory
from apps.domains.sticky.models.sticky import Sticky
from apps.domains.workplace.models import Workplace, WorkplaceMember
from lib.utils.fractional_indexing import generate_key_between

DEFAULT_COUNT = 20
TRASH_CHANCE = 0.15


class Command(BaseCommand):
    help = "Seeds a workplace with realistic fake stickies, for exercising the stickies board/trash UI."

    def add_arguments(self, parser):
        parser.add_argument(
            "--workplace",
            type=int,
            default=None,
            help="Workplace id to seed. Defaults to the oldest workplace.",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=DEFAULT_COUNT,
            help=f"Number of stickies to create (default: {DEFAULT_COUNT}).",
        )

    def handle(self, *args, **options):
        workplace = self._get_workplace(options["workplace"])
        count = options["count"]

        members = list(WorkplaceMember.objects.filter(workplace=workplace))
        if not members:
            raise CommandError("Workplace has no members — cannot seed realistic stickies.")

        # Same fractional-index append logic as StickyViewSet.perform_create.
        last_position = (
            Sticky.objects.filter(workplace=workplace)
            .exclude(position="")
            .order_by("-position")
            .values_list("position", flat=True)
            .first()
        )

        trashed = 0

        for _ in range(count):
            last_position = generate_key_between(last_position, None)
            is_trashed = random.random() < TRASH_CHANCE
            if is_trashed:
                trashed += 1

            StickyFactory(
                workplace=workplace,
                created_by=random.choice(members).user,
                position=last_position,
                trashed=is_trashed,
                deleted_by=random.choice(members).user if is_trashed else None,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {count} sticky(ies) in workplace '{workplace.name}' ({trashed} sent to trash)."
            )
        )

    def _get_workplace(self, workplace_id: int | None) -> Workplace:
        if workplace_id is not None:
            try:
                return Workplace.objects.get(pk=workplace_id)
            except Workplace.DoesNotExist as exc:
                raise CommandError(f"Workplace {workplace_id} not found.") from exc

        workplace = Workplace.objects.order_by("id").first()
        if workplace is None:
            raise CommandError("No workplace found — create one first.")
        return workplace
