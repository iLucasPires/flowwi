from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from lib.models import TimeStampedModel, UUIDModel

from .document import Document
from .version import DocumentVersion

User = get_user_model()


class DocumentFeedbackDecision(models.IntegerChoices):
    LIKE = 1, _("Like")
    DISLIKE = 2, _("Dislike")


class DocumentFeedback(TimeStampedModel, UUIDModel):
    """Feedback (like/dislike) on the document or a specific version."""

    document = models.ForeignKey(
        to=Document,
        related_name="feedbacks",
        on_delete=models.CASCADE,
        verbose_name=_("document"),
        help_text=_("The document receiving feedback."),
    )

    version = models.ForeignKey(
        to=DocumentVersion,
        related_name="feedbacks",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("version"),
        help_text=_("The specific version receiving feedback, if any."),
    )

    given_by = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name=_("given by"),
        help_text=_("The user who gave the feedback."),
    )

    decision = models.IntegerField(
        verbose_name=_("decision"),
        choices=DocumentFeedbackDecision.choices,
        default=DocumentFeedbackDecision.LIKE,
        help_text=_("The feedback decision (like or dislike)."),
    )

    notes = models.TextField(
        verbose_name=_("notes"),
        blank=True,
        help_text=_("Additional notes or reasons for the feedback."),
    )

    class Meta:
        unique_together = (
            "document",
            "version",
            "given_by",
        )
        verbose_name = _("Feedback")
        verbose_name_plural = _("Feedbacks")

    def __str__(self):
        return f"{self.get_decision_display()} — Document #{self.document_id}"
