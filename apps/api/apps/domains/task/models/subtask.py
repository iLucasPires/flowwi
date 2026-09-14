from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.domains.workplace.models import WorkplaceMember
from lib.models import TimeStampedModel, UUIDModel

from .task import Task


class SubTask(
    TimeStampedModel,
    UUIDModel,
):
    title = models.CharField(
        max_length=200,
        verbose_name=_("title"),
        help_text=_("The title of the subtask."),
    )

    is_done = models.BooleanField(
        default=False,
        verbose_name=_("is done"),
        help_text=_("Whether the subtask is completed."),
    )

    position = models.CharField(
        max_length=100,
        default="",
        blank=True,
        verbose_name=_("position"),
        help_text=_("Fractional index for ordering within the parent task."),
    )

    assignee = models.ForeignKey(
        to=WorkplaceMember,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("assignee"),
        help_text=_("The member responsible for this subtask."),
    )

    task = models.ForeignKey(
        to=Task,
        related_name="subs",
        on_delete=models.CASCADE,
        verbose_name=_("task"),
        help_text=_("The parent task for this subtask."),
    )

    class Meta:
        verbose_name = _("Subtask")
        verbose_name_plural = _("Subtasks")

    def __str__(self):
        return self.title
