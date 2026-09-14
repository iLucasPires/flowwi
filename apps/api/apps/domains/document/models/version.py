from django.db import models
from django.utils.translation import gettext_lazy as _

from lib.models import TimeStampedModel, UUIDModel

from .document import Document


def empty_document() -> dict:
    """Historical default, referenced by migration 0001/0003. Content is a list[str] now."""
    return {"type": "doc", "content": []}


class DocumentVersionStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PUBLISHED = "published", _("Published")


class DocumentVersion(TimeStampedModel, UUIDModel):
    """A revision of a Document's content. The latest version is autosaved as it's edited."""

    number = models.PositiveSmallIntegerField(
        verbose_name=_("number"),
        default=1,
        db_index=True,
        help_text=_("The version number (e.g., 1, 2, 3)."),
    )

    status = models.CharField(
        verbose_name=_("status"),
        max_length=16,
        choices=DocumentVersionStatus.choices,
        default=DocumentVersionStatus.DRAFT,
        help_text=_(
            "Draft versions are freely editable but cannot receive comments. "
            "Published versions are read-only until switched back to draft.",
        ),
    )

    content = models.JSONField(
        verbose_name=_("content"),
        blank=True,
        default=str,
        help_text=_(
            "The document content for this version, as a markdown string "
            "(supports '[[Title]]' wiki-links to other documents).",
        ),
    )

    document = models.ForeignKey(
        to=Document,
        related_name="versions",
        on_delete=models.CASCADE,
        verbose_name=_("document"),
        help_text=_("The document this version belongs to."),
    )

    class Meta:
        ordering = ["-number"]
        unique_together = ("document", "number")
        verbose_name = _("Version")
        verbose_name_plural = _("Versions")

    def __str__(self):
        return f"v{self.number} — Document #{self.document_id}"
