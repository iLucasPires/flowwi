from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from lib.models import (
    CoverStyleModel,
    CreatedModel,
    TimeStampedSoftDeleteModel,
    UUIDModel,
)
from lib.utils.upload import upload_to_path

from ..utils import generate_invite_key

User = get_user_model()


class Workplace(
    TimeStampedSoftDeleteModel,
    UUIDModel,
    CreatedModel,
    CoverStyleModel,
):
    name = models.CharField(
        max_length=200,
        verbose_name=_("name"),
        help_text=_("The name of the workplace."),
    )

    slug = models.SlugField(
        unique=True,
        verbose_name=_("slug"),
        help_text=_("A unique slug used in URLs."),
    )

    photo = models.ImageField(
        upload_to=upload_to_path(
            "workplaces",
            "photos",
        ),
        blank=True,
        null=True,
        verbose_name=_("photo"),
        help_text=_("The profile photo or logo for this workplace."),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
        help_text=_("Whether this workplace is currently active."),
    )

    invite_key = models.CharField(
        max_length=8,
        unique=True,
        default=generate_invite_key,
        verbose_name=_("invite key"),
        help_text=_("Unique key used to invite members to this workplace."),
    )

    ai_usage_tokens = models.BigIntegerField(default=0)
    ai_limit_tokens = models.BigIntegerField(default=1_000_000)

    class Meta:
        verbose_name = _("Workplace")
        verbose_name_plural = _("Workplaces")

    def __str__(self):
        return self.name

    def get_storage_workplace(self):
        return self

    def is_owner(self, user: User) -> bool:
        return self.members.filter(
            role="owner",
            user=user,
        ).exists()

    def is_manager(self, user: User) -> bool:
        return self.members.filter(
            role="manager",
            user=user,
        ).exists()

    def is_designer(self, user: User) -> bool:
        return self.members.filter(
            role="designer",
            user=user,
        ).exists()

    @property
    def storage_percent_used(self) -> float:
        try:
            return self.storage_used / self.storage_limit
        except ZeroDivisionError:
            return 0.0

    @property
    def ai_usage_tokens_percent(self) -> float:
        try:
            return self.ai_usage_tokens / self.ai_limit_tokens
        except ZeroDivisionError:
            return 0.0
