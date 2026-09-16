from rest_framework import serializers

from ..models.sticky import Sticky


class StickySerializer(serializers.ModelSerializer):
    class Meta:
        model = Sticky
        fields = [
            "id",
            "workplace",
            "created_by",
            "visibility",
            "color",
            "text",
            "position",
            "created_at",
            "updated_at",
            "deleted_at",
            "deleted_by",
        ]
        read_only_fields = [
            "workplace",
            "created_by",
            "position",
            "created_at",
            "updated_at",
            "deleted_at",
            "deleted_by",
        ]
