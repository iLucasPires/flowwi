from django.db import migrations

PRESETS = [
    {
        "name": "Minimalista",
        "accent_color": "neutral",
        "radius": "sm",
        "input_size": "md",
        "font": "sans",
        "cover_style": "#fafaf9",
    },
    {
        "name": "Moderno",
        "accent_color": "blue",
        "radius": "lg",
        "input_size": "md",
        "font": "sans",
        "cover_style": "#eff6ff",
    },
    {
        "name": "Vibrante",
        "accent_color": "violet",
        "radius": "xl",
        "input_size": "lg",
        "font": "sans",
        "cover_style": "linear-gradient(135deg, #a78bfa 0%, #f472b6 100%)",
    },
    {
        "name": "Editorial",
        "accent_color": "neutral",
        "radius": "none",
        "input_size": "md",
        "font": "serif",
        "cover_style": "#f5f5f4",
    },
]


def seed_presets(apps, schema_editor):
    FormTheme = apps.get_model("form", "FormTheme")
    for preset in PRESETS:
        FormTheme.objects.get_or_create(
            name=preset["name"],
            is_preset=True,
            workplace=None,
            defaults=preset,
        )


def remove_presets(apps, schema_editor):
    FormTheme = apps.get_model("form", "FormTheme")
    FormTheme.objects.filter(is_preset=True, name__in=[p["name"] for p in PRESETS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("form", "0004_formtheme_form_theme"),
    ]

    operations = [
        migrations.RunPython(seed_presets, remove_presets),
    ]
