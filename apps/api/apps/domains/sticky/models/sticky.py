from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.domains.workplace.models import Workplace
from lib.models import TimeStampedSoftDeleteModel, UUIDModel

User = get_user_model()


class StickyVisibility(models.TextChoices):
    PRIVATE = "private", _("Private")
    WORKFLOW = "workplace", _("Workplace")


class Sticky(
    TimeStampedSoftDeleteModel,
    UUIDModel,
):
    workplace = models.ForeignKey(
        to=Workplace,
        related_name="stickies",
        on_delete=models.CASCADE,
        verbose_name=_("workplace"),
        help_text=_("The workplace this sticky belongs to."),
    )

    created_by = models.ForeignKey(
        to=User,
        related_name="created_stickies",
        on_delete=models.CASCADE,
        verbose_name=_("created by"),
        help_text=_("User who created this sticky."),
    )

    deleted_by = models.ForeignKey(
        to=User,
        related_name="deleted_stickies",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("deleted by"),
        help_text=_("User who deleted this sticky."),
    )

    visibility = models.CharField(
        max_length=20,
        choices=StickyVisibility.choices,
        default=StickyVisibility.PRIVATE,
        verbose_name=_("visibility"),
        help_text=_("Who can see this sticky."),
    )

    color = models.CharField(
        max_length=7,
        default="#FEE440",
        verbose_name=_("color"),
        help_text=_("Hexadecimal color code for the sticky."),
    )

    text = models.TextField(
        blank=True,
        verbose_name=_("text"),
        help_text=_("The sticky content."),
    )

    position = models.CharField(
        max_length=100,
        default="",
        blank=True,
        verbose_name=_("position"),
        help_text=_("Fractional index for ordering stickies."),
    )

    class Meta(
        TimeStampedSoftDeleteModel.Meta,
        UUIDModel.Meta,
    ):
        verbose_name = _("Sticky")
        verbose_name_plural = _("Stickies")
        indexes = [
            models.Index(fields=["workplace", "deleted_at"]),
            models.Index(fields=["workplace", "visibility", "deleted_at"]),
            models.Index(fields=["workplace", "created_by", "deleted_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.workplace} - {self.created_by} ({self.visibility})"
