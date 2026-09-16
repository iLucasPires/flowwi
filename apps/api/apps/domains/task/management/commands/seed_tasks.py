import random
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.domains.task.factories import TaskFactory, weighted_choice
from apps.domains.task.models import TaskStatus, TaskStatusCategory, TaskType
from apps.domains.workplace.models import Workplace, WorkplaceMember
from lib.utils.fractional_indexing import generate_key_between

DEFAULT_COUNT = 100
TRASH_CHANCE = 0.08
ASSIGNEE_CHANCE = 0.8
DEADLINE_CHANCE = 0.7


class Command(BaseCommand):
    help = "Seeds a workplace with realistic fake tasks, for exercising the task board/list/trash UI."

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
            help=f"Number of tasks to create (default: {DEFAULT_COUNT}).",
        )

    def handle(self, *args, **options):
        workplace = self._get_workplace(options["workplace"])
        count = options["count"]

        statuses = list(TaskStatus.objects.filter(workplace=workplace))
        types = list(TaskType.objects.filter(workplace=workplace))
        members = list(WorkplaceMember.objects.filter(workplace=workplace))

        if not statuses or not types or not members:
            raise CommandError("Workplace is missing statuses, types or members — cannot seed realistic tasks.")

        status_weights = [(s, 5 if s.category != TaskStatusCategory.CANCELLED else 1) for s in statuses]

        # Track the last position used per status so seeded tasks stack in order,
        # matching how TaskSerializer.create() appends new tasks on the board.
        last_position_by_status: dict[int, str | None] = dict.fromkeys((s.id for s in statuses), None)

        now = timezone.now()
        trashed = 0

        for _ in range(count):
            status = weighted_choice(status_weights)
            deadline = None
            if random.random() < DEADLINE_CHANCE:
                deadline = (now + timedelta(days=random.randint(-20, 45))).date()

            completed_at = None
            if status.category == TaskStatusCategory.DONE:
                completed_at = now - timedelta(days=random.randint(0, 30))

            position = generate_key_between(last_position_by_status[status.id], None)
            last_position_by_status[status.id] = position

            is_trashed = random.random() < TRASH_CHANCE
            if is_trashed:
                trashed += 1

            assignees = (
                random.sample(members, min(len(members), random.choice([1, 1, 2])))
                if random.random() < ASSIGNEE_CHANCE
                else []
            )

            TaskFactory(
                workplace=workplace,
                type=random.choice(types),
                status=status,
                created_by=random.choice(members),
                position=position,
                deadline=deadline,
                completed_at=completed_at,
                assignees=assignees,
                trashed=is_trashed,
                deleted_by=random.choice(members).user if is_trashed else None,
            )

        self.stdout.write(
            self.style.SUCCESS(f"Created {count} task(s) in workplace '{workplace.name}' ({trashed} sent to trash).")
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
