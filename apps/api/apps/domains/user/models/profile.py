from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from lib.models import CoverStyleModel, FileCleanupModel, TimeStampedModel, UUIDModel
from lib.utils.upload import upload_to_path


class Profile(UUIDModel, TimeStampedModel, FileCleanupModel, CoverStyleModel):
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("user"),
        help_text=_("The user associated with this profile."),
    )

    photo = models.ImageField(
        upload_to=upload_to_path("profiles", "photos"),
        blank=True,
        null=True,
        verbose_name=_("photo"),
        help_text=_("The user's profile photo."),
    )

    cover = models.ImageField(
        upload_to=upload_to_path("profiles", "covers"),
        blank=True,
        null=True,
        verbose_name=_("cover"),
        help_text=_("The user's profile cover image."),
    )

    file_fields = ("photo", "cover")

    class Meta:
        unique_together = ("user",)
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self) -> str:
        return f"{self.user}"

    @property
    def username(self) -> str | None:
        return getattr(self.user, "username", None)

    @property
    def email(self) -> str | None:
        return getattr(self.user, "email", None)

    @property
    def full_name(self) -> str | None:
        name = self.user.get_full_name()
        return name or getattr(self.user, "username", None)
