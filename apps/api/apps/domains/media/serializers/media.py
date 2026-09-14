from rest_framework import serializers

from ..models import (
    Media,
    MediaComment,
    MediaFeedback,
    MediaVersion,
)


class MediaSerializer(serializers.ModelSerializer):
    class MediaNestedVersionSerializer(serializers.ModelSerializer):
        file = serializers.SerializerMethodField()

        def get_file(self, obj) -> str:
            if obj.drive_file_id:
                return f"https://lh3.googleusercontent.com/d/{obj.drive_file_id}"

            return obj.drive_url or ""

        class Meta:
            model = MediaVersion
            fields = ["id", "media", "file", "text_content", "number", "type", "created_at"]
            read_only_fields = ["created_at"]

    class MediaNestedFeedbackSerializer(serializers.ModelSerializer):
        class Meta:
            model = MediaFeedback
            fields = ["id", "media", "version", "given_by", "decision", "created_at"]
            read_only_fields = ["created_at", "given_by"]

    class MediaNestedCommentSerializer(serializers.ModelSerializer):
        class Meta:
            model = MediaComment
            fields = [
                "id",
                "media",
                "version",
                "author",
                "guest_name",
                "content",
                "block_index",
                "quote",
                "created_at",
            ]
            read_only_fields = ["created_at", "author", "guest_name"]

    versions = MediaNestedVersionSerializer(many=True, read_only=True)
    feedbacks = MediaNestedFeedbackSerializer(many=True, read_only=True)
    comments = MediaNestedCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Media
        fields = [
            "id",
            "task",
            "designer",
            "title",
            "notes",
            "type",
            "is_approved",
            "share_token",
            "versions",
            "feedbacks",
            "comments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "designer", "share_token"]
