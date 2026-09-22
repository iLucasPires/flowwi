from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from lib.models import TimeStampedModel, UUIDModel

from ..validators import validate_form_config
from .form import Form
from .page import FormPage


class FormBlockType(models.TextChoices):
    TEXT = "text", _("Text")
    EMAIL = "email", _("Email")
    NUMBER = "number", _("Number")
    TIME = "time", _("Time")
    DATE = "date", _("Date")
    FILE = "file", _("File")
    CHOICE = "choice", _("Choice")
    SELECT = "select", _("Select")
    CONTENT = "content", _("Content")
    PHONE = "phone", _("Phone")
    URL = "url", _("URL")
    YES_NO = "yes_no", _("Yes/No")
    RATING = "rating", _("Rating")
    SCALE = "scale", _("Scale")
    SLIDER = "slider", _("Slider")
    RANKING = "ranking", _("Ranking")
    COUNTRY = "country", _("Country")
    SIGNATURE = "signature", _("Signature")


class FormBlock(UUIDModel, TimeStampedModel):
    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
    )

    type = models.CharField(
        max_length=50,
        choices=FormBlockType.choices,
        verbose_name=_("type"),
    )

    required = models.BooleanField(
        default=False,
        verbose_name=_("required"),
    )

    order = models.IntegerField(
        default=0,
        verbose_name=_("order"),
    )

    config = models.JSONField(
        default=dict,
        verbose_name=_("configuration"),
    )

    col_span = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("column span"),
    )

    col_start = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("column start"),
    )

    condition = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("condition"),
        help_text=_(
            "Visibility condition. Either a single condition "
            "`{field_id, operator, value}` or a group "
            "`{op:'and'|'or', rules:[...]}` for advanced logic."
        ),
    )

    default_value = models.JSONField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_("default value"),
        help_text=_("Default value pre-filled for the respondent."),
    )

    prefix = models.CharField(
        max_length=32,
        blank=True,
        default="",
        verbose_name=_("prefix"),
        help_text=_("Prefix label shown before the input (e.g. 'R$', 'US$')."),
    )

    suffix = models.CharField(
        max_length=32,
        blank=True,
        default="",
        verbose_name=_("suffix"),
        help_text=_("Suffix label shown after the input (e.g. 'kg', '%', 'years')."),
    )

    logic_jump = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("logic jump"),
        help_text=_(
            "Jump rules mapping answer values → target page order (or 'end'). "
            "Example: `{\"yes\": 2, \"no\": \"end\"}` — when this block is answered, "
            "jump to page 2 or finish the form."
        ),
    )

    client_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name=_("client id"),
    )

    form = models.ForeignKey(
        to=Form,
        related_name="blocks",
        on_delete=models.CASCADE,
        verbose_name=_("form"),
    )

    page = models.ForeignKey(
        to=FormPage,
        related_name="blocks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("page"),
    )

    class Meta:
        ordering = ["page__order", "order"]
        unique_together = ["form", "page", "order"]
        verbose_name = _("Form Block")
        verbose_name_plural = _("Form Blocks")

    def __str__(self):
        return f"{self.form.title} - {self.title}"

    def clean(self):
        validate_form_config(self.type, self.config)

        if self.page and self.page.form_id != self.form_id:
            raise ValidationError(_("Page must belong to the same form."))

    @property
    def options(self):
        if self.type in {FormBlockType.CHOICE, FormBlockType.SELECT}:
            return self.get("options", [])
        return []
