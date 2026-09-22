from rest_framework import serializers

from ..models import Form, FormBlock, FormPage


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
            "default_value",
            "prefix",
            "suffix",
            "logic_jump",
            "client_id",
        ]


class PublicPageSerializer(serializers.ModelSerializer):
    blocks = serializers.SerializerMethodField()

    class Meta:
        model = FormPage
        fields = [
            "id",
            "title",
            "description",
            "order",
            "cover_image",
            "cover_style",
            "cover_credit",
            "blocks",
        ]

    def get_blocks(self, obj):
        return PublicBlockSerializer(obj.blocks.order_by("order"), many=True).data


class FormPublicSerializer(serializers.ModelSerializer):
    blocks = serializers.SerializerMethodField()
    pages = serializers.SerializerMethodField()

    class Meta:
        model = Form
        fields = [
            "id",
            "public_id",
            "title",
            "icon",
            "description",
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
            "blocks",
            "pages",
        ]

    def get_blocks(self, obj):
        return PublicBlockSerializer(obj.blocks.order_by("page__order", "order"), many=True).data

    def get_pages(self, obj):
        return PublicPageSerializer(obj.pages.order_by("order"), many=True).data
