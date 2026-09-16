from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.domains.workplace.models import Workplace, WorkplaceMember
from lib.models import TimeStampedSoftDeleteModel, UUIDModel

from .status import TaskStatus
from .tag import TaskTag
from .type import TaskType

User = get_user_model()


class TaskPriority(models.TextChoices):
    LOW = "low", _("Low")
    MEDIUM = "medium", _("Medium")
    HIGH = "high", _("High")
    URGENT = "urgent", _("Urgent")


class TaskOrigin(models.TextChoices):
    INTERNAL = "internal", _("Internal")
    EXTERNAL = "external", _("External")


class Task(TimeStampedSoftDeleteModel, UUIDModel):
    title = models.CharField(
        max_length=200,
        verbose_name=_("title"),
        help_text=_("Short and clear title describing the task."),
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
        help_text=_("Detailed description of what needs to be done."),
    )

    type = models.ForeignKey(
        to=TaskType,
        related_name="tasks",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("type"),
        help_text=_("Category of the task."),
    )

    position = models.CharField(
        max_length=100,
        default="",
        blank=True,
        verbose_name=_("position"),
        help_text=_("Fractional index for ordering within its current status."),
    )

    status = models.ForeignKey(
        to=TaskStatus,
        related_name="tasks",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("status"),
        help_text=_("Current workplace status of the task."),
    )

    priority = models.CharField(
        max_length=10,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM,
        verbose_name=_("priority"),
        help_text=_("Priority level used to organize or escalate tasks."),
    )

    origin = models.CharField(
        max_length=10,
        choices=TaskOrigin.choices,
        default=TaskOrigin.INTERNAL,
        verbose_name=_("origin"),
        help_text=_("Defines whether the task was created internally or requested externally."),
    )

    deadline = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("deadline"),
        help_text=_("Optional due date for the task."),
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("completed at"),
        help_text=_("Timestamp automatically filled when the task is completed."),
    )

    created_by = models.ForeignKey(
        to=WorkplaceMember,
        related_name="created_tasks",
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_("created by"),
        help_text=_("User who created the task."),
    )

    assignees = models.ManyToManyField(
        to=WorkplaceMember,
        related_name="tasks",
        blank=True,
        verbose_name=_("assignees"),
        help_text=_("Users responsible for executing this task."),
    )

    deleted_by = models.ForeignKey(
        to=User,
        related_name="deleted_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("deleted by"),
        help_text=_("User who deleted the task."),
    )

    workplace = models.ForeignKey(
        to=Workplace,
        related_name="tasks",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("workplace"),
        help_text=_("The workplace this task belongs to."),
    )

    tags = models.ManyToManyField(
        to=TaskTag,
        blank=True,
        related_name="tasks",
        verbose_name=_("tags"),
        help_text=_("Tags used to categorize or group this task."),
    )

    class Meta(
        TimeStampedSoftDeleteModel.Meta,
        UUIDModel.Meta,
    ):
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
        indexes = [
            models.Index(fields=["workplace", "deleted_at"]),
            models.Index(fields=["workplace", "status", "deleted_at"]),
        ]

    def __str__(self):
        type_label = self.type.name if self.type_id else _("No type")
        return f"[{type_label}] {self.title}"
