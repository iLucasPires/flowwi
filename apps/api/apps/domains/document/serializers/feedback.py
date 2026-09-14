from rest_framework import serializers

from ..models import DocumentFeedback


class DocumentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFeedback
        fields = ["id", "document", "version", "given_by", "decision", "created_at"]
        read_only_fields = ["created_at", "given_by"]

    def get_validators(self):
        return []
