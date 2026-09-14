from enum import StrEnum

from pydantic import BaseModel, Field

# =============================================================================
# Enums (mirror the model's TextChoices — see models/theme.py)
# =============================================================================


class ThemeAccentColor(StrEnum):
    NEUTRAL = "neutral"
    RED = "red"
    ORANGE = "orange"
    AMBER = "amber"
    GREEN = "green"
    EMERALD = "emerald"
    CYAN = "cyan"
    BLUE = "blue"
    INDIGO = "indigo"
    VIOLET = "violet"
    PINK = "pink"


class ThemeRadius(StrEnum):
    NONE = "none"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"


class ThemeInputSize(StrEnum):
    SM = "sm"
    MD = "md"
    LG = "lg"


class ThemeFont(StrEnum):
    SANS = "sans"
    SERIF = "serif"
    MONO = "mono"


# =============================================================================
# Agent output
# =============================================================================


class GeneratedTheme(BaseModel):
    name: str
    accent_color: ThemeAccentColor = ThemeAccentColor.NEUTRAL
    radius: ThemeRadius = ThemeRadius.MD
    input_size: ThemeInputSize = ThemeInputSize.MD
    font: ThemeFont = ThemeFont.SANS
    background_style: str = Field(
        default="",
        description="CSS color or gradient for the background (e.g. '#f5f5f4' or "
        "'linear-gradient(135deg, #667eea, #764ba2)'). Empty for no background override.",
    )
    custom_css: str = Field(
        default="",
        description="Optional advanced CSS rules, scoped under a '.ft-root' ancestor selector.",
    )
