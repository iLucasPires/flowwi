from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.domains.task.models import Task
from apps.domains.workplace.models import Workplace
from lib.models import CoverStyleModel, TimeStampedModel, UUIDModel
from lib.utils.upload import upload_to_path

from .type import DocumentType

User = get_user_model()


class DocumentVisibility(models.TextChoices):
    PRIVATE = "private", _("Private")
    WORKPLACE = "workplace", _("Workplace")


class Document(TimeStampedModel, UUIDModel, CoverStyleModel):
    """
    A written document — supports comments, feedback, and revision history.

    Sharing is object-level, enforced via django-guardian (see `apps.document.signals`
    and `apps.document.permissions`): the author and workplace admins (owner/manager)
    always have full access, regardless of `visibility`/`allow_member_edit` — those two
    fields only control what *other* workplace members get.
    """

    title = models.CharField(
        verbose_name=_("title"),
        max_length=255,
        blank=True,
        help_text=_("The title of the document."),
    )

    icon = models.CharField(
        verbose_name=_("icon"),
        max_length=50,
        blank=True,
        default="",
        help_text=_("Icon identifier (e.g. i-lucide-file-text) or a literal emoji character."),
    )

    cover = models.ImageField(
        verbose_name=_("cover"),
        upload_to=upload_to_path("documents", "covers"),
        blank=True,
        null=True,
        help_text=_("Uploaded banner image shown at the top of the document."),
    )

    notes = models.TextField(
        verbose_name=_("notes"),
        blank=True,
        help_text=_("Internal notes about the document."),
    )

    folder = models.CharField(
        verbose_name=_("folder"),
        max_length=255,
        blank=True,
        default="",
        help_text=_(
            "Slash-separated vault folder path for this document (e.g. 'Clientes/Café Origem'). "
            "Blank means the document sits at the vault root.",
        ),
    )

    visibility = models.CharField(
        max_length=20,
        choices=DocumentVisibility.choices,
        default=DocumentVisibility.WORKPLACE,
        verbose_name=_("visibility"),
        help_text=_(
            "Who besides the author and workplace admins can see this document: every workplace member, or nobody else."
        ),
    )

    allow_member_edit = models.BooleanField(
        default=False,
        verbose_name=_("allow member edit"),
        help_text=_(
            "Whether workplace members who can view this document may also edit it "
            "(the author and workplace admins can always edit, regardless of this)."
        ),
    )

    workplace = models.ForeignKey(
        to=Workplace,
        null=True,
        blank=True,
        related_name="documents",
        on_delete=models.CASCADE,
        verbose_name=_("workplace"),
        help_text=_("The workplace this document belongs to."),
    )

    task = models.ForeignKey(
        to=Task,
        null=True,
        blank=True,
        related_name="documents",
        on_delete=models.SET_NULL,
        verbose_name=_("task"),
        help_text=_("The task this document belongs to (optional)."),
    )

    type = models.ForeignKey(
        to=DocumentType,
        null=True,
        blank=True,
        related_name="documents",
        on_delete=models.SET_NULL,
        verbose_name=_("type"),
        help_text=_("The type/category of this document."),
    )

    author = models.ForeignKey(
        to=User,
        related_name="authored_documents",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("author"),
        help_text=_("The user who created this document."),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")

    def __str__(self):
        return self.title or f"Document #{self.pk}"
