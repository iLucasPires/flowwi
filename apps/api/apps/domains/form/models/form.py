from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.domains.workplace.models import Workplace
from lib.models import TimeStampedModel, UUIDModel


class FormLayout(models.TextChoices):
    MULTI_QUESTION = "multi", _("Multi-question page")
    SINGLE_QUESTION = "single", _("One question per screen (Tally-style)")


class FormThemePreset(models.TextChoices):
    DEFAULT = "default", _("Default")
    DARK = "dark", _("Dark")
    MINIMAL = "minimal", _("Minimal")
    BRANDED = "branded", _("Branded")


class Form(
    UUIDModel,
    TimeStampedModel,
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

    # --- Tally-inspired advanced settings ---

    layout_mode = models.CharField(
        max_length=16,
        choices=FormLayout.choices,
        default=FormLayout.MULTI_QUESTION,
        verbose_name=_("layout mode"),
        help_text=_(
            "'multi' = multiple questions per page (classic). "
            "'single' = one question per full screen (Tally/Typeform style)."
        ),
    )

    close_message = models.TextField(
        blank=True,
        default="",
        verbose_name=_("close message"),
        help_text=_(
            "Custom thank-you / completion message shown on the final screen "
            "after a successful submission."
        ),
    )

    redirect_url = models.URLField(
        blank=True,
        default="",
        verbose_name=_("redirect URL"),
        help_text=_(
            "Optional URL the respondent is redirected to after submitting. "
            "When set, overrides the default completion screen."
        ),
    )

    thankyou_redirect_delay = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("thank-you redirect delay"),
        help_text=_(
            "Seconds to wait on the thank-you screen before redirecting "
            "(0 = redirect immediately, when redirect_url is set)."
        ),
    )

    max_responses = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_("max responses"),
        help_text=_(
            "Optional cap on how many total submissions are accepted. "
            "Once reached, the form closes and shows the closed message."
        ),
    )

    closed_message = models.TextField(
        blank=True,
        default="",
        verbose_name=_("closed message"),
        help_text=_(
            "Custom message displayed when the form is closed "
            "(e.g. max_responses reached or manually closed)."
        ),
    )

    allow_multiple = models.BooleanField(
        default=False,
        verbose_name=_("allow multiple responses"),
        help_text=_("Whether the same visitor can submit the form multiple times."),
    )

    progress_bar_enabled = models.BooleanField(
        default=True,
        verbose_name=_("progress bar enabled"),
        help_text=_(
            "Show the animated progress bar at the top of the public form."
        ),
    )

    theme_preset = models.CharField(
        max_length=32,
        choices=FormThemePreset.choices,
        default=FormThemePreset.DEFAULT,
        verbose_name=_("theme preset"),
        help_text=_("Visual theme preset applied to the public form."),
    )

    theme = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("theme overrides"),
        help_text=_(
            "Fine-grained theme overrides: `{accent_color, bg_color, text_color, "
            "font_family, button_style, radius}`. Applied on top of `theme_preset`."
        ),
    )

    captcha_enabled = models.BooleanField(
        default=False,
        verbose_name=_("captcha enabled"),
        help_text=_("Require a CAPTCHA challenge before submitting."),
    )

    public_id = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        blank=True,
        default="",
        verbose_name=_("public id"),
        help_text=_("Slug/UUID used in the public share URL."),
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

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Form")
        verbose_name_plural = _("Forms")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.public_id:
            import secrets
            self.public_id = secrets.token_urlsafe(10)
        super().save(*args, **kwargs)

    def get_storage_workplace(self):
        return self.workplace
