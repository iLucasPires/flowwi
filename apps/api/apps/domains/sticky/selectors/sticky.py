from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet

from apps.domains.workplace.models import Workplace

from ..models.sticky import Sticky, StickyVisibility

User = get_user_model()


class StickySelector:
    @staticmethod
    def for_workplace(workplace: Workplace, *, trashed: bool = False) -> QuerySet[Sticky]:
        return Sticky.objects.filter(
            workplace=workplace,
            deleted_at__isnull=not trashed,
        )

    @staticmethod
    def for_user(workplace: Workplace, user, *, trashed: bool = False) -> QuerySet[Sticky]:
        return StickySelector.for_workplace(workplace, trashed=trashed).filter(
            Q(visibility=StickyVisibility.WORKFLOW) | Q(created_by=user),
        )
