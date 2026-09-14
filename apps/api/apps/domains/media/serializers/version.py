from rest_framework import serializers

from ..models import MediaComment, MediaFeedback, MediaVersion


class MediaVersionSerializer(serializers.ModelSerializer):
    class MediaVersionNestedFeedbackSerializer(serializers.ModelSerializer):
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

    class MediaVersionNestedCommentSerializer(serializers.ModelSerializer):
        class Meta:
            model = MediaComment
            fields = [
                "id",
                "media",
                "version",
                "author",
                "content",
                "block_index",
                "quote",
                "created_at",
            ]
            read_only_fields = [
                "created_at",
                "author",
            ]

    feedbacks = MediaVersionNestedFeedbackSerializer(many=True, read_only=True)
    comments = MediaVersionNestedCommentSerializer(many=True, read_only=True)

    file = serializers.SerializerMethodField()

    def get_file(self, obj) -> str:
        if obj.drive_file_id:
            return f"https://lh3.googleusercontent.com/d/{obj.drive_file_id}"

        return obj.drive_url or ""

    class Meta:
        model = MediaVersion
        fields = [
            "id",
            "media",
            "number",
            "type",
            "file",
            "text_content",
            "drive_file_id",
            "file_name",
            "mime_type",
            "feedbacks",
            "comments",
            "created_at",
        ]
        read_only_fields = [
            "number",
            "drive_file_id",
            "drive_url",
            "file_name",
            "mime_type",
            "created_at",
        ]

    def get_validators(self):
        return []
