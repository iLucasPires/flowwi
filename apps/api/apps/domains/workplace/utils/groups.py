from django.contrib.auth.models import Group


def workplace_members_group_name(workplace_id: int | str) -> str:
    """Deterministic name for the Django Group mirroring a workplace's membership."""
    return f"workplace-{workplace_id}-members"


def get_workplace_members_group(workplace_id: int | str) -> Group:
    """
    The Group used to grant django-guardian permissions to "everyone in this workplace"
    in one row, instead of one permission row per member per document. Kept in sync with
    `WorkplaceMember` via signals (see `apps.workplace.signals`).
    """
    group, _ = Group.objects.get_or_create(name=workplace_members_group_name(workplace_id))

    return group
