from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.domains.workplace.models import WorkplaceMember
from lib.models import TimeStampedModel, UUIDModel


class InboxType(models.IntegerChoices):
    SYSTEM = 1, _("System")
    ORDER = 2, _("Order")
    MESSAGE = 3, _("Message")
    TASK_ASSIGNED = 4, _("Task Assigned")
    MEDIA_COMMENT = 5, _("Media Comment")
    MEMBER_JOINED = 6, _("Member Joined")


class Inbox(UUIDModel, TimeStampedModel):
    member = models.ForeignKey(
        to=WorkplaceMember,
        on_delete=models.CASCADE,
        related_name="inboxes",
        verbose_name=_("member"),
        help_text=_("The workplace member who owns this inbox entry."),
    )

    sender = models.ForeignKey(
        to=WorkplaceMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_inboxes",
        verbose_name=_("sender"),
        help_text=_("The workplace member who created this notification."),
    )

    type = models.PositiveSmallIntegerField(
        choices=InboxType.choices,
        default=InboxType.SYSTEM,
        verbose_name=_("type"),
        help_text=_("The type of the inbox notification."),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
        help_text=_("The title of the notification."),
    )

    message = models.TextField(
        verbose_name=_("message"),
        help_text=_("The body content of the notification."),
    )

    is_read = models.BooleanField(
        default=False,
        verbose_name=_("is read"),
        help_text=_("Whether the user has read this notification."),
    )

    class Meta(UUIDModel.Meta, TimeStampedModel.Meta):
        verbose_name = _("Inbox")
        verbose_name_plural = _("Inboxes")

        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["member", "is_read"]),
            models.Index(fields=["type"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.member})"
