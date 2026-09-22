# Generated manually — removes FormTheme model and the theme FK on Form.

import django.db.models.deletion
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("form", "0006_remove_form_cover_credit_remove_form_cover_image_and_more"),
        ("workplace", "0001_initial"),
    ]

    operations = [
        # 1. Drop the FK column on Form first (before dropping the referenced table)
        migrations.RemoveField(
            model_name="form",
            name="theme",
        ),
        # 2. Drop the FormTheme table
        migrations.DeleteModel(
            name="FormTheme",
        ),
    ]
