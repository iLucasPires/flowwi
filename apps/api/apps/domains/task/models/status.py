from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.domains.workplace.models import Workplace
from lib.models import TimeStampedModel, UUIDModel


class TaskStatusCategory(models.TextChoices):
    TODO = "todo", _("To Do")
    IN_PROGRESS = "in_progress", _("In Progress")
    DONE = "done", _("Done")
    CANCELLED = "cancelled", _("Cancelled")


class TaskStatus(
    UUIDModel,
    TimeStampedModel,
):
    name = models.CharField(
        max_length=50,
        verbose_name=_("name"),
        help_text=_("The name of the status."),
    )
    color = models.CharField(
        max_length=7,
        default="#5CFCD4",
        verbose_name=_("color"),
        help_text=_("Hexadecimal color code for the status."),
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name=_("icon"),
        help_text=_("Icon identifier for the status (e.g. i-lucide-circle-dashed)."),
    )
    category = models.CharField(
        max_length=20,
        choices=TaskStatusCategory.choices,
        verbose_name=_("category"),
        help_text=_("Fixed category used to derive workflow semantics (todo/in progress/done/cancelled)."),
    )
    position = models.CharField(
        max_length=100,
        default="",
        blank=True,
        verbose_name=_("position"),
        help_text=_("Fractional index for ordering within its workplace."),
    )

    workplace = models.ForeignKey(
        to=Workplace,
        related_name="task_statuses",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("workplace"),
        help_text=_("The workplace this status belongs to."),
    )

    class Meta:
        ordering = ["position"]
        verbose_name = _("Task Status")
        verbose_name_plural = _("Task Statuses")

    def __str__(self):
        return self.name
