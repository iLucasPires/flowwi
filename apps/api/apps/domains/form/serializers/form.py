from rest_framework import serializers

from lib.serializers import ExpandableSerializerModel

from ..models import Form


class FormSerializer(ExpandableSerializerModel, serializers.ModelSerializer):
    responses_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Form
        fields = [
            "id",
            "workplace",
            "title",
            "icon",
            "description",
            "is_published",
            "created_at",
            "public_id",
            "require_auth",
            "require_identity",
            "grid_columns",
            "layout_mode",
            "close_message",
            "redirect_url",
            "thankyou_redirect_delay",
            "max_responses",
            "closed_message",
            "allow_multiple",
            "progress_bar_enabled",
            "theme_preset",
            "theme",
            "captcha_enabled",
            "responses_count",
        ]
        read_only_fields = [
            "id",
            "public_id",
            "workplace",
            "created_at",
        ]
