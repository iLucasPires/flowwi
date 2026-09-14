from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import WorkplaceMember
from .utils import get_workplace_members_group


@receiver(post_save, sender=WorkplaceMember)
def add_member_to_workplace_group(sender, instance: WorkplaceMember, created: bool, **kwargs):
    """Keeps the workplace's Group in sync, so guardian's group permissions cover every
    member automatically — the group is what `Document.visibility = WORKPLACE` grants
    `view_document` to (see `apps.document.signals`)."""
    if not created:
        return

    group = get_workplace_members_group(instance.workplace_id)
    instance.user.groups.add(group)


@receiver(post_delete, sender=WorkplaceMember)
def remove_member_from_workplace_group(sender, instance: WorkplaceMember, **kwargs):
    group = get_workplace_members_group(instance.workplace_id)
    instance.user.groups.remove(group)
