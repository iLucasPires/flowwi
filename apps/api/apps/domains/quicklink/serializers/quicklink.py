from rest_framework import serializers

from ..models import QuickLink


class QuickLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuickLink
        fields = [
            "id",
            "workplace",
            "title",
            "url",
            "icon",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "workplace",
            "created_by",
            "created_at",
            "updated_at",
        ]
