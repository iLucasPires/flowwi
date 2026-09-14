from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from lib.models import TimeStampedModel, UUIDModel

from .media import Media
from .version import MediaVersion

User = get_user_model()


class MediaFeedbackDecision(models.IntegerChoices):
    LIKE = 1, _("Like")
    DISLIKE = 2, _("Dislike")


class MediaFeedback(TimeStampedModel, UUIDModel):
    """Feedback (like/dislike) on the media or a specific version."""

    media = models.ForeignKey(
        to=Media,
        related_name="feedbacks",
        on_delete=models.CASCADE,
        verbose_name=_("media"),
        help_text=_("The media receiving feedback."),
    )

    version = models.ForeignKey(
        to=MediaVersion,
        related_name="feedbacks",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("version"),
        help_text=_("The specific version receiving feedback, if any."),
    )

    given_by = models.ForeignKey(
        to="auth.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("given by"),
        help_text=_(
            "The user who gave the feedback. Null for feedback left through the public share "
            "link — unlike the authenticated path, there's no stable identity to dedupe on, so "
            "each anonymous vote is its own row (the unique constraint below only applies "
            "between non-null values)."
        ),
    )

    decision = models.IntegerField(
        verbose_name=_("decision"),
        choices=MediaFeedbackDecision.choices,
        default=MediaFeedbackDecision.LIKE,
        help_text=_("The feedback decision (like or dislike)."),
    )

    notes = models.TextField(
        verbose_name=_("notes"),
        blank=True,
        help_text=_("Additional notes or reasons for the feedback."),
    )

    class Meta:
        unique_together = (
            "media",
            "version",
            "given_by",
        )
        verbose_name = _("Feedback")
        verbose_name_plural = _("Feedbacks")
        db_table = "art_artfeedback"

    def __str__(self):
        return f"{self.get_decision_display()} — Media #{self.media_id}"
