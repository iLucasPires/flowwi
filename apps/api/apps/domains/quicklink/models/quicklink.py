from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.domains.workplace.models import Workplace, WorkplaceMember
from lib.models import TimeStampedModel


class QuickLink(TimeStampedModel):
    workplace = models.ForeignKey(
        to=Workplace,
        related_name="quicklinks",
        on_delete=models.CASCADE,
        verbose_name=_("workplace"),
        help_text=_("The workplace this quicklink belongs to."),
    )

    title = models.CharField(
        max_length=100,
        verbose_name=_("title"),
        help_text=_("Short label shown on the Home page."),
    )

    url = models.URLField(
        verbose_name=_("url"),
        help_text=_("The link's destination."),
    )

    icon = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("icon"),
        help_text=_("Optional Lucide icon name shown next to the title."),
    )

    created_by = models.ForeignKey(
        to=WorkplaceMember,
        related_name="created_quicklinks",
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_("created by"),
        help_text=_("Member who added this quicklink."),
    )

    class Meta(TimeStampedModel.Meta):
        verbose_name = _("Quicklink")
        verbose_name_plural = _("Quicklinks")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workplace", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.workplace})"
