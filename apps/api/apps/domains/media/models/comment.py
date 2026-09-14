from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from lib.models import TimeStampedModel, UUIDModel

from .media import Media
from .version import MediaVersion

User = get_user_model()


class MediaComment(TimeStampedModel, UUIDModel):
    """Discussion on the media or a specific version."""

    media = models.ForeignKey(
        to=Media,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name=_("media"),
        help_text=_("The media being commented on."),
    )

    version = models.ForeignKey(
        to=MediaVersion,
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
        help_text=_("The user who wrote the comment. Null for a comment left through the public share link."),
    )

    guest_name = models.CharField(
        max_length=150,
        blank=True,
        default="",
        verbose_name=_("guest name"),
        help_text=_(
            "Display name for a comment left through the public share link, where there's no "
            "authenticated user to attribute it to. Blank whenever `author` is set."
        ),
    )

    content = models.TextField(
        verbose_name=_("content"),
        help_text=_("The content of the comment."),
    )

    block_index = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_("block index"),
        help_text=_(
            "Position anchor for the comment, meaning depends on media type — e.g. a timestamp in "
            "seconds for video versions. Null means a general (non-anchored) comment."
        ),
    )

    quote = models.TextField(
        blank=True,
        default="",
        verbose_name=_("quote"),
        help_text=_(
            "The selected text snippet this comment is anchored to, for text versions. Blank means a general comment."
        ),
    )

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        db_table = "art_artcomment"

    def __str__(self):
        return self.content[:50]
