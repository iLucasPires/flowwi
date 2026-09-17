from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from lib.models import TimeStampedModel, UUIDModel

from .workplace import Workplace

User = get_user_model()


class WorkplaceMemberRole(models.TextChoices):
    OWNER = "owner", _("Owner")
    MANAGER = "manager", _("Manager")
    DESIGNER = "designer", _("Designer")


class WorkplaceMemberStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    ACTIVE = "active", _("Active")


class WorkplaceMember(TimeStampedModel, UUIDModel):
    workplace = models.ForeignKey(
        to=Workplace,
        related_name="members",
        on_delete=models.CASCADE,
        verbose_name=_("workplace"),
        help_text=_("The workplace this member belongs to."),
    )

    user = models.ForeignKey(
        to=User,
        related_name="workplace_memberships",
        on_delete=models.CASCADE,
        verbose_name=_("user"),
        help_text=_("The user who is a member of the workplace."),
    )

    role = models.CharField(
        max_length=10,
        choices=WorkplaceMemberRole.choices,
        default=WorkplaceMemberRole.DESIGNER,
        verbose_name=_("role"),
        help_text=_("The role of the member within the workplace."),
    )

    status = models.CharField(
        max_length=10,
        choices=WorkplaceMemberStatus.choices,
        default=WorkplaceMemberStatus.ACTIVE,
        verbose_name=_("status"),
        help_text=_("Whether this membership is active or still awaiting admin approval."),
    )

    class Meta(TimeStampedModel.Meta, UUIDModel.Meta):
        unique_together = ("workplace", "user")
        verbose_name = _("Member")
        verbose_name_plural = _("Members")

    def __str__(self):
        return f"{self.user} - {self.workplace} ({self.role})"
