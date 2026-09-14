from django.core.exceptions import ValidationError

BLOCKED_CUSTOM_CSS_PATTERNS = ("@import", "<script", "expression(")


def validate_custom_css(value: str):
    """Minimal guardrail: block the obvious tracking/script injection vectors. The rest of
    `custom_css` is trusted the same way a workplace's rich-text form description already is —
    it's the workplace's own public form, rendered scoped under `.ft-root` (see `@scope` usage
    in the frontend's `formThemeScopedCss`)."""
    lowered = value.lower()
    for pattern in BLOCKED_CUSTOM_CSS_PATTERNS:
        if pattern in lowered:
            raise ValidationError(f"CSS não pode conter '{pattern}'.")
