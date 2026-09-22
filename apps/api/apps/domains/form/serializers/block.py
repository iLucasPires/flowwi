from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models import FormBlock
from ..validators import validate_form_condition, validate_form_config


class FormBlockSerializer(serializers.ModelSerializer):
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

    def validate(self, attrs):
        self._validate_page_belongs_to_form(attrs)
        self._validate_config(attrs)
        self._validate_condition(attrs)

        return attrs

    def _validate_page_belongs_to_form(self, attrs):
        page = attrs.get("page")

        if not page:
            return

        form = attrs.get("form") or getattr(self.instance, "form", None)
        if form and page.form_id != form.id:
            raise serializers.ValidationError({"page": "Page must belong to the same form."})

    def _validate_config(self, attrs):
        block_type = attrs.get("type")

        if not block_type:
            return

        try:
            validate_form_config(block_type, attrs.get("config") or {})
        except DjangoValidationError as e:
            raise serializers.ValidationError({"config": e.messages}) from e

    def _validate_condition(self, attrs):
        condition = attrs.get("condition")
        if not condition:
            return

        try:
            validate_form_condition(condition)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"condition": e.messages}) from e
