from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.domains.workplace.models import Workplace
from lib.models import TimeStampedModel, UUIDModel

User = get_user_model()


class GoogleDriveConnection(TimeStampedModel, UUIDModel):
    """OAuth connection to Google Drive for a workplace."""

    workplace = models.ForeignKey(
        to=Workplace,
        related_name="drive_connections",
        on_delete=models.CASCADE,
        verbose_name=_("workplace"),
    )

    connected_by = models.ForeignKey(
        to=User,
        related_name="drive_connections",
        on_delete=models.CASCADE,
        verbose_name=_("connected by"),
    )

    access_token = models.TextField(
        verbose_name=_("access token"),
        help_text=_("Google OAuth2 access token."),
    )

    refresh_token = models.TextField(
        verbose_name=_("refresh token"),
        help_text=_("Google OAuth2 refresh token."),
    )

    token_expires_at = models.DateTimeField(
        verbose_name=_("token expires at"),
        null=True,
        blank=True,
    )

    folder_id = models.CharField(
        verbose_name=_("folder ID"),
        max_length=255,
        blank=True,
        help_text=_("Google Drive folder ID to sync from."),
    )

    is_active = models.BooleanField(
        verbose_name=_("is active"),
        default=True,
    )

    class Meta:
        verbose_name = _("Google Drive Connection")
        verbose_name_plural = _("Google Drive Connections")

    def __str__(self):
        return f"Drive — {self.workplace} (by {self.connected_by})"
