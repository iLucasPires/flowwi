from rest_framework import serializers

from ..models import FormTheme
from ..validators import validate_custom_css


class FormThemeSerializer(serializers.ModelSerializer):
    def validate_custom_css(self, value):
        validate_custom_css(value)
        return value

    class Meta:
        model = FormTheme
        fields = [
            "id",
            "workplace",
            "name",
            "is_preset",
            "background_image",
            "cover_style",
            "cover_credit",
            "accent_color",
            "radius",
            "input_size",
            "font",
            "custom_css",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "workplace",
            "is_preset",
            "created_at",
        ]
