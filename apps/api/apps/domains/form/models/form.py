from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.domains.workplace.models import Workplace
from lib.models import CoverStyleModel, TimeStampedModel, UUIDModel
from lib.utils.upload import upload_to_path


class Form(
    UUIDModel,
    TimeStampedModel,
    CoverStyleModel,
):
    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
        help_text=_("The title of the form."),
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name=_("icon"),
        help_text=_("Icon identifier (e.g. i-lucide-file-text) or a literal emoji character."),
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
        help_text=_("A detailed description of the form's purpose."),
    )

    is_published = models.BooleanField(
        default=False,
        verbose_name=_("is published"),
        help_text=_("Whether the form is publicly available."),
    )

    cover_image = models.ImageField(
        upload_to=upload_to_path("forms", "covers"),
        null=True,
        blank=True,
        verbose_name=_("cover image"),
        help_text=_("A cover image to be displayed at the top of the form."),
    )

    require_auth = models.BooleanField(
        default=False,
        verbose_name=_("require authentication"),
        help_text=_("Whether users must be logged in to submit the form."),
    )

    require_identity = models.BooleanField(
        default=False,
        verbose_name=_("require identity"),
        help_text=_("Whether to collect respondent identity information."),
    )

    grid_columns = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_("grid columns"),
        help_text=_("Number of columns in the form layout grid."),
    )

    workplace = models.ForeignKey(
        to=Workplace,
        related_name="forms",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("workplace"),
        help_text=_("The workplace this form belongs to."),
    )

    theme = models.ForeignKey(
        to="form.FormTheme",
        related_name="forms",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("theme"),
        help_text=_("Visual theme applied to the public form."),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Form")
        verbose_name_plural = _("Forms")

    def __str__(self):
        return self.title

    def get_storage_workplace(self):
        return self.workplace
