from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.domains.workplace.models import Workplace
from lib.models import CoverStyleModel, TimeStampedModel, UUIDModel
from lib.utils.upload import upload_to_path

from ..validators import validate_custom_css


class FormThemeAccentColor(models.TextChoices):
    """Mirrors `cAccentColorItems` in the frontend (`shared/composables/accentColor.ts`) —
    keeping this list in sync there is what lets the theme scope the same
    `--ui-color-primary-*` override mechanism already used for the app-wide accent color,
    just applied to the public form wrapper instead of `document.documentElement`."""

    NEUTRAL = "neutral", _("Neutral")
    RED = "red", _("Red")
    ORANGE = "orange", _("Orange")
    AMBER = "amber", _("Amber")
    GREEN = "green", _("Green")
    EMERALD = "emerald", _("Emerald")
    CYAN = "cyan", _("Cyan")
    BLUE = "blue", _("Blue")
    INDIGO = "indigo", _("Indigo")
    VIOLET = "violet", _("Violet")
    PINK = "pink", _("Pink")


class FormThemeRadius(models.TextChoices):
    NONE = "none", _("None")
    SM = "sm", _("Small")
    MD = "md", _("Medium")
    LG = "lg", _("Large")
    XL = "xl", _("Extra large")


class FormThemeInputSize(models.TextChoices):
    SM = "sm", _("Small")
    MD = "md", _("Medium")
    LG = "lg", _("Large")


class FormThemeFont(models.TextChoices):
    SANS = "sans", _("Sans-serif")
    SERIF = "serif", _("Serif")
    MONO = "mono", _("Monospace")


class FormTheme(
    UUIDModel,
    TimeStampedModel,
    CoverStyleModel,
):
    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
        help_text=_("The name of the theme."),
    )

    is_preset = models.BooleanField(
        default=False,
        verbose_name=_("is preset"),
        help_text=_("Whether this is a built-in theme, shared with every workplace."),
    )

    background_image = models.ImageField(
        upload_to=upload_to_path("form-themes", "backgrounds"),
        null=True,
        blank=True,
        verbose_name=_("background image"),
        help_text=_("A background image for the public form. Takes precedence over cover_style."),
    )

    accent_color = models.CharField(
        max_length=20,
        choices=FormThemeAccentColor.choices,
        default=FormThemeAccentColor.NEUTRAL,
        verbose_name=_("accent color"),
        help_text=_("Accent color for buttons, links and progress indicators."),
    )

    radius = models.CharField(
        max_length=10,
        choices=FormThemeRadius.choices,
        default=FormThemeRadius.MD,
        verbose_name=_("radius"),
        help_text=_("Border radius applied to inputs, buttons and cards."),
    )

    input_size = models.CharField(
        max_length=10,
        choices=FormThemeInputSize.choices,
        default=FormThemeInputSize.MD,
        verbose_name=_("input size"),
        help_text=_("Size applied to inputs, selects and buttons."),
    )

    font = models.CharField(
        max_length=10,
        choices=FormThemeFont.choices,
        default=FormThemeFont.SANS,
        verbose_name=_("font"),
        help_text=_("Font family applied to the public form."),
    )

    custom_css = models.TextField(
        blank=True,
        default="",
        verbose_name=_("custom CSS"),
        help_text=_("Advanced CSS overrides, scoped to the public form wrapper."),
    )

    workplace = models.ForeignKey(
        to=Workplace,
        related_name="form_themes",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("workplace"),
        help_text=_("The workplace this theme belongs to. Null for built-in presets."),
    )

    class Meta:
        ordering = ["-is_preset", "-created_at"]
        verbose_name = _("Form Theme")
        verbose_name_plural = _("Form Themes")

    def __str__(self):
        return self.name

    def clean(self):
        validate_custom_css(self.custom_css)

    def get_storage_workplace(self):
        return self.workplace
