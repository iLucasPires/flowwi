from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.domains.workplace.models import Workplace
from lib.models import TimeStampedModel, UUIDModel

User = get_user_model()


class TaskTag(
    UUIDModel,
    TimeStampedModel,
):
    name = models.CharField(
        max_length=50,
        verbose_name=_("name"),
        help_text=_("The name of the tag."),
    )
    color = models.CharField(
        max_length=7,
        default="#5CFCD4",
        verbose_name=_("color"),
        help_text=_("Hexadecimal color code for the tag."),
    )

    workplace = models.ForeignKey(
        to=Workplace,
        related_name="task_tags",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("workplace"),
        help_text=_("The workplace this tag belongs to."),
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.name
