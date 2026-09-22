from django.db import models
from django.utils.translation import gettext_lazy as _

from lib.models import CoverStyleModel, TimeStampedModel, UUIDModel
from lib.utils.upload import upload_to_path

from .form import Form


class FormPage(UUIDModel, TimeStampedModel, CoverStyleModel):
    title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("title"),
        help_text=_("Optional title shown at the top of this page."),
    )

    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("description"),
        help_text=_("Optional description or instructions for this page."),
    )

    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("order"),
        help_text=_("Display order of this page within the form."),
    )

    cover_image = models.ImageField(
        upload_to=upload_to_path("forms", "covers"),
        null=True,
        blank=True,
        verbose_name=_("cover image"),
        help_text=_("A cover image to be displayed at the top of this page."),
    )

    form = models.ForeignKey(
        to=Form,
        related_name="pages",
        on_delete=models.CASCADE,
        verbose_name=_("form"),
        help_text=_("The form this page belongs to."),
    )

    class Meta:
        ordering = ["order"]
        unique_together = ["form", "order"]
        verbose_name = _("Form Page")
        verbose_name_plural = _("Form Pages")

    def __str__(self):
        return f"{self.form.title} — Page {self.order + 1}"
