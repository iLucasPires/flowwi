from rest_framework import serializers

from ..models import DocumentComment, DocumentFeedback, DocumentVersion, DocumentVersionStatus


class DocumentVersionSerializer(serializers.ModelSerializer):
    class DocumentVersionNestedFeedbackSerializer(serializers.ModelSerializer):
        class Meta:
            model = DocumentFeedback
            fields = ["id", "document", "version", "given_by", "decision", "created_at"]
            read_only_fields = ["created_at", "given_by"]

    class DocumentVersionNestedCommentSerializer(serializers.ModelSerializer):
        class Meta:
            model = DocumentComment
            fields = ["id", "document", "version", "author", "content", "block_index", "quote", "created_at"]
            read_only_fields = ["created_at", "author"]

    feedbacks = DocumentVersionNestedFeedbackSerializer(many=True, read_only=True)
    comments = DocumentVersionNestedCommentSerializer(many=True, read_only=True)

    class Meta:
        model = DocumentVersion
        fields = [
            "id",
            "document",
            "number",
            "content",
            "status",
            "feedbacks",
            "comments",
            "created_at",
        ]
        read_only_fields = ["number", "created_at"]

    def get_validators(self):
        return []

    def validate(self, attrs):
        instance = self.instance
        stays_published = (
            instance
            and instance.status == DocumentVersionStatus.PUBLISHED
            and attrs.get("status", instance.status) == DocumentVersionStatus.PUBLISHED
        )
        if stays_published and "content" in attrs:
            raise serializers.ValidationError(
                {"content": "Published versions are read-only. Switch back to draft to edit."},
            )
        return attrs
