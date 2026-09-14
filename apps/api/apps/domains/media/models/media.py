import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.domains.task.models import Task
from apps.domains.workplace.models import Workplace
from lib.models import TimeStampedModel, UUIDModel

User = get_user_model()


class MediaType(models.IntegerChoices):
    IMAGE = 1, _("Image")
    VIDEO = 2, _("Video")
    DOCUMENT = 3, _("Document")
    ART = 4, _("Art")


class Media(TimeStampedModel, UUIDModel):
    """A media deliverable — produced for a task. Supports images, videos, documents, and art."""

    title = models.CharField(
        verbose_name=_("title"),
        max_length=255,
        blank=True,
        help_text=_("The title of the media deliverable."),
    )

    notes = models.TextField(
        verbose_name=_("notes"),
        blank=True,
        help_text=_("Internal notes about the media."),
    )

    type = models.PositiveSmallIntegerField(
        verbose_name=_("type"),
        choices=MediaType.choices,
        default=MediaType.ART,
        help_text=_("The type of media (image, video, document, art)."),
    )

    is_approved = models.BooleanField(
        verbose_name=_("is approved"),
        default=False,
        help_text=_("Whether this media has been approved by the requester."),
    )

    share_token = models.UUIDField(
        verbose_name=_("share token"),
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        help_text=_("Public token used for sharing the media with external stakeholders."),
    )

    workplace = models.ForeignKey(
        to=Workplace,
        null=True,
        blank=True,
        related_name="medias",
        on_delete=models.CASCADE,
        verbose_name=_("workplace"),
        help_text=_("The workplace this media belongs to."),
    )

    task = models.ForeignKey(
        to=Task,
        null=True,
        blank=True,
        related_name="medias",
        on_delete=models.SET_NULL,
        verbose_name=_("task"),
        help_text=_("The task this media belongs to (optional)."),
    )

    designer = models.ForeignKey(
        to=User,
        related_name="produced_medias",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("designer"),
        help_text=_("The designer who produced this media."),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Media")
        verbose_name_plural = _("Media")
        db_table = "art_art"

    def __str__(self):
        return f"Media #{self.pk} — Task {self.task_id}"
