from rest_framework import serializers

from ..models import MediaFeedback


class MediaFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFeedback
        fields = [
            "id",
            "media",
            "version",
            "given_by",
            "decision",
            "created_at",
        ]
        read_only_fields = [
            "created_at",
            "given_by",
        ]

    def get_validators(self):
        return []
