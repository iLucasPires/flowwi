from rest_framework import serializers

from ..models import Media, MediaComment, MediaFeedback, MediaVersion


class MediaPublicCommentSerializer(serializers.ModelSerializer):
    """Input for a comment left through the public share link (no `media`/`author` —
    `media` comes from the `share_token` in the URL, `author` is always null here)."""

    class Meta:
        model = MediaComment
        fields = ["version", "content", "block_index", "quote", "guest_name"]

    def validate_guest_name(self, value: str) -> str:
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Informe seu nome.")

        return value

    def validate_content(self, value: str) -> str:
        value = value.strip()

        if not value:
            raise serializers.ValidationError("O comentário não pode ficar vazio.")

        return value


class MediaPublicFeedbackSerializer(serializers.ModelSerializer):
    """Input for feedback left through the public share link — same reasoning as
    `MediaPublicCommentSerializer` for what's excluded (`media`, `given_by`)."""

    class Meta:
        model = MediaFeedback
        fields = ["version", "decision"]

    def get_validators(self):
        return []


class _MediaPublicNestedVersionSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    def get_file(self, obj: MediaVersion) -> str:
        if obj.drive_file_id:
            return f"https://lh3.googleusercontent.com/d/{obj.drive_file_id}"

        return obj.drive_url or ""

    class Meta:
        model = MediaVersion
        fields = ["id", "media", "file", "text_content", "number", "type", "created_at"]
        read_only_fields = fields


class _MediaPublicNestedFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFeedback
        fields = ["id", "media", "version", "decision", "created_at"]
        read_only_fields = fields


class _MediaPublicNestedCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaComment
        fields = ["id", "media", "version", "author", "guest_name", "content", "block_index", "quote", "created_at"]
        read_only_fields = fields


class MediaPublicSerializer(serializers.ModelSerializer):
    """
    What a guest on the public share link (`apps.media.views.public`) sees —
    a deliberately trimmed subset of `MediaSerializer`'s fields: no `task`, `designer`,
    `workplace`, or `share_token` echoed back. Read-only — comments/feedback are
    written through their own dedicated views/serializers above, not through this one.
    """

    versions = _MediaPublicNestedVersionSerializer(many=True, read_only=True)
    feedbacks = _MediaPublicNestedFeedbackSerializer(many=True, read_only=True)
    comments = _MediaPublicNestedCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Media
        fields = ["id", "title", "notes", "is_approved", "versions", "feedbacks", "comments", "created_at"]
        read_only_fields = fields
