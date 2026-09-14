from rest_framework import serializers

from ..models import Form, FormBlock, FormPage
from .theme import FormThemeSerializer


class PublicBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormBlock
        fields = [
            "id",
            "form",
            "page",
            "title",
            "type",
            "required",
            "order",
            "config",
            "col_span",
            "col_start",
            "condition",
            "client_id",
        ]


class PublicPageSerializer(serializers.ModelSerializer):
    blocks = serializers.SerializerMethodField()

    class Meta:
        model = FormPage
        fields = ["id", "title", "description", "order", "blocks"]

    def get_blocks(self, obj):
        return PublicBlockSerializer(obj.blocks.order_by("order"), many=True).data


class FormPublicSerializer(serializers.ModelSerializer):
    blocks = serializers.SerializerMethodField()
    pages = serializers.SerializerMethodField()
    theme = serializers.SerializerMethodField()

    class Meta:
        model = Form
        fields = [
            "id",
            "public_id",
            "title",
            "icon",
            "description",
            "cover_image",
            "cover_style",
            "cover_credit",
            "require_auth",
            "require_identity",
            "grid_columns",
            "blocks",
            "pages",
            "theme",
        ]

    def get_blocks(self, obj):
        return PublicBlockSerializer(obj.blocks.order_by("page__order", "order"), many=True).data

    def get_pages(self, obj):
        return PublicPageSerializer(obj.pages.order_by("order"), many=True).data

    def get_theme(self, obj):
        # Always nested (not gated by `?expand=`, unlike FormSerializer) — the public page
        # always needs the full theme to render, there's no "IDs only" use case here.
        return FormThemeSerializer(obj.theme).data if obj.theme else None
