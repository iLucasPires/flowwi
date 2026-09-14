from rest_framework import serializers

from ..models import DocumentType


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = [
            "id",
            "name",
            "color",
            "icon",
            "position",
            "default_content",
            "workplace",
        ]
        read_only_fields = [
            "position",
            "workplace",
        ]
