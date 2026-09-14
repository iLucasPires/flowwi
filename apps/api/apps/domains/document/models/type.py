from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.domains.workplace.models import Workplace
from lib.models import TimeStampedModel, UUIDModel


class DocumentType(
    UUIDModel,
    TimeStampedModel,
):
    name = models.CharField(
        max_length=50,
        verbose_name=_("name"),
        help_text=_("The name of the type."),
    )
    color = models.CharField(
        max_length=7,
        default="#5CFCD4",
        verbose_name=_("color"),
        help_text=_("Hexadecimal color code for the type."),
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name=_("icon"),
        help_text=_("Icon identifier for the type (e.g. i-lucide-palette)."),
    )
    position = models.CharField(
        max_length=100,
        default="",
        blank=True,
        verbose_name=_("position"),
        help_text=_("Fractional index for ordering within its workplace."),
    )

    default_content = models.TextField(
        blank=True,
        default="",
        verbose_name=_("default content"),
        help_text=_(
            "Starting markdown content used to seed a new document's first version "
            "when created with this type. Blank means the document starts empty."
        ),
    )

    workplace = models.ForeignKey(
        to=Workplace,
        related_name="document_types",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("workplace"),
        help_text=_("The workplace this type belongs to."),
    )

    class Meta:
        ordering = ["position"]
        verbose_name = _("Document Type")
        verbose_name_plural = _("Document Types")

    def __str__(self):
        return self.name
