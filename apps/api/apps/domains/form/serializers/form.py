from rest_framework import serializers

from lib.serializers import ExpandableSerializerModel

from ..models import Form
from .theme import FormThemeSerializer


class FormSerializer(ExpandableSerializerModel, serializers.ModelSerializer):
    # Annotated on the viewset's queryset (`Count("responses", distinct=True)`) so the
    # list view doesn't have to nest every response just to show a count on the card.
    responses_count = serializers.IntegerField(read_only=True, default=0)

    expandable_fields = {
        "theme": lambda: FormThemeSerializer(read_only=True),
    }

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
            "cover_image",
            "cover_style",
            "cover_credit",
            "require_auth",
            "require_identity",
            "grid_columns",
            "responses_count",
            "theme",
        ]
        read_only_fields = [
            "id",
            "public_id",
            "workplace",
            "created_at",
        ]
