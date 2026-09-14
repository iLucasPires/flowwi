from django.db.models import Q, QuerySet

from apps.domains.workplace.models import Workplace

from ..models import FormTheme


class FormThemeSelector:
    @staticmethod
    def for_workplace(workplace: Workplace | None) -> QuerySet[FormTheme]:
        """Every preset plus the workplace's own themes — `None` returns presets only."""
        if not workplace:
            return FormTheme.objects.filter(is_preset=True)

        return FormTheme.objects.filter(Q(workplace=workplace) | Q(is_preset=True))
