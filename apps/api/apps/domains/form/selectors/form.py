from collections import Counter
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from ..models import Form, FormAnswer


class FormSelector:
    @staticmethod
    def get_public(public_id: str) -> Form | None:
        return (
            Form.objects.select_related("theme")
            .prefetch_related(
                "pages",
                "pages__blocks",
                "blocks",
            )
            .filter(
                public_id=public_id,
                is_published=True,
            )
            .first()
        )

    @staticmethod
    def count_answered(form: Form) -> dict[int, int]:
        """How many non-empty answers each block received."""
        rows = (
            FormAnswer.objects.filter(response__form=form)
            .exclude(value__in=[None, "", []])
            .values("block_id")
            .annotate(total=Count("id"))
            .values_list("block_id", "total")
        )

        return dict(rows)

    @staticmethod
    def count_options(form: Form, block_ids: list[int]) -> dict[int, list[dict]]:
        """For choice/select blocks, count how often each option was picked."""
        if not block_ids:
            return {}

        answers = FormAnswer.objects.filter(
            block_id__in=block_ids,
            response__form=form,
        ).values_list(
            "block_id",
            "value",
        )

        counters: dict[int, Counter] = {}
        for block_id, value in answers:
            if not value:
                continue

            counter = counters.setdefault(block_id, Counter())
            if isinstance(value, list):
                counter.update(str(v) for v in value if v)
            else:
                counter[str(value)] += 1

        return {
            block_id: [
                {
                    "label": label,
                    "count": count,
                }
                for label, count in counter.most_common()
            ]
            for block_id, counter in counters.items()
        }

    @staticmethod
    def count_submissions(form: Form, days: int = 30) -> list[dict]:
        """Daily submission count for the last N days."""
        since = timezone.now() - timedelta(days=days)
        rows = (
            form.responses.filter(created_at__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
            .values_list("day", "count")
        )

        return [
            {
                "date": str(day),
                "count": count,
            }
            for day, count in rows
        ]
