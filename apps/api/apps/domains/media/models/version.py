from django.db import models
from django.utils.translation import gettext_lazy as _

from lib.models import TimeStampedModel, UUIDModel

from .media import Media


class MediaVersionType(models.IntegerChoices):
    IMAGE = 1, _("Image")
    VIDEO = 2, _("Video")
    FILE = 3, _("File")
    LINK = 4, _("Link")
    TEXT = 5, _("Text")
    DOCUMENT = 6, _("Document")


class MediaVersion(TimeStampedModel, UUIDModel):
    """A single file revision of a Media, stored in Google Drive."""

    number = models.PositiveSmallIntegerField(
        verbose_name=_("number"),
        default=1,
        db_index=True,
        help_text=_("The version number (e.g., 1, 2, 3)."),
    )

    type = models.PositiveSmallIntegerField(
        verbose_name=_("type"),
        choices=MediaVersionType.choices,
        default=MediaVersionType.IMAGE,
        help_text=_("The type of file for this version."),
    )

    drive_file_id = models.CharField(
        verbose_name=_("Drive file ID"),
        max_length=255,
        blank=True,
        help_text=_("Google Drive file ID."),
    )

    drive_url = models.URLField(
        verbose_name=_("Drive URL"),
        max_length=500,
        blank=True,
        help_text=_("Direct view/download URL from Google Drive."),
    )

    file_name = models.CharField(
        verbose_name=_("file name"),
        max_length=255,
        blank=True,
        help_text=_("Original file name."),
    )

    mime_type = models.CharField(
        verbose_name=_("MIME type"),
        max_length=127,
        blank=True,
        help_text=_("MIME type of the file."),
    )

    text_content = models.TextField(
        blank=True,
        default="",
        verbose_name=_("text content"),
        help_text=_("Raw text content for text-type versions, edited directly in the app."),
    )

    media = models.ForeignKey(
        to=Media,
        related_name="versions",
        on_delete=models.CASCADE,
        verbose_name=_("media"),
        help_text=_("The media this version belongs to."),
    )

    class Meta:
        ordering = ["-number"]
        unique_together = ("media", "number")
        verbose_name = _("Version")
        verbose_name_plural = _("Versions")
        db_table = "art_artversion"

    def __str__(self):
        return f"v{self.number} — Media #{self.media_id}"
