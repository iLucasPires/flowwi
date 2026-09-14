from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from lib.models import TimeStampedModel, UUIDModel

from .document import Document
from .version import DocumentVersion

User = get_user_model()


class DocumentComment(TimeStampedModel, UUIDModel):
    """Discussion on the document or a specific version."""

    document = models.ForeignKey(
        to=Document,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name=_("document"),
        help_text=_("The document being commented on."),
    )

    version = models.ForeignKey(
        to=DocumentVersion,
        related_name="comments",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("version"),
        help_text=_("The specific version being commented on, if any."),
    )

    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("author"),
        help_text=_("The user who wrote the comment."),
    )

    content = models.TextField(
        verbose_name=_("content"),
        help_text=_("The content of the comment."),
    )

    block_index = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("block index"),
        help_text=_(
            "Line index in the version's content this comment is anchored to. "
            "Null means a general (non-anchored) comment.",
        ),
    )

    quote = models.TextField(
        blank=True,
        default="",
        verbose_name=_("quote"),
        help_text=_(
            "The selected text snippet this comment is anchored to, if any. Blank means a general comment.",
        ),
    )

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    def __str__(self):
        return self.content[:50]
