from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.common.streaming.publisher import publish_to_user

from .models import Inbox
from .services import InboxService


@receiver(post_save, sender=Inbox)
def publish_inbox_created(sender, instance, created, **kwargs):
    if not created:
        return

    inbox_service = InboxService()

    # Keyed by the stable User.id (not the WorkplaceMember.id) so the push
    # reaches the recipient's SSE connection regardless of which workplace
    # they currently have active — see `apps.common.streaming.publisher.publish_to_user`.
    publish_to_user(
        user_id=instance.member.user_id,
        event="inbox-notification",
        data=inbox_service.build_inbox_payload(instance),
    )
