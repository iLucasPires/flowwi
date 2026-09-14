from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.common.streaming.publisher import publish_event

from .models import Inbox
from .services import InboxService


@receiver(post_save, sender=Inbox)
def publish_inbox_created(sender, instance, created, **kwargs):
    if not created:
        return

    inbox_service = InboxService()

    publish_event(
        channel=inbox_service.channel_name(instance.member_id),
        event="inbox-notification",
        data=inbox_service.build_inbox_payload(instance),
    )
