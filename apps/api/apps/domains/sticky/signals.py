from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.common.streaming.publisher import publish_resource_changed

from .models.sticky import Sticky


@receiver(post_save, sender=Sticky)
def notify_sticky_changed(sender, instance, created, **kwargs):
    action = "deleted" if instance.deleted_at else ("created" if created else "updated")
    publish_resource_changed(instance.workplace_id, "sticky", action, instance.id)


@receiver(post_delete, sender=Sticky)
def notify_sticky_purged(sender, instance, **kwargs):
    publish_resource_changed(instance.workplace_id, "sticky", "deleted", instance.id)
