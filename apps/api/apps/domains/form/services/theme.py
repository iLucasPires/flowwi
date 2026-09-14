from django.core.files.base import ContentFile

from lib.bases import ServiceBase

from ..models import FormTheme


class FormThemeService(ServiceBase):
    def __init__(self):
        super().__init__(model=FormTheme)

    def duplicate(self, theme: FormTheme, workplace) -> FormTheme:
        """Copy a theme (typically a preset) into an editable theme owned by `workplace`."""
        copy = FormTheme.objects.create(
            workplace=workplace,
            is_preset=False,
            name=f"{theme.name} (cópia)",
            cover_style=theme.cover_style,
            cover_credit=theme.cover_credit,
            accent_color=theme.accent_color,
            radius=theme.radius,
            input_size=theme.input_size,
            font=theme.font,
            custom_css=theme.custom_css,
        )

        if theme.background_image:
            copy.background_image.save(
                theme.background_image.name.rsplit("/", 1)[-1],
                ContentFile(theme.background_image.read()),
                save=True,
            )

        return copy
