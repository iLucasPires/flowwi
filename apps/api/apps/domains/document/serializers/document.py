from rest_framework import serializers

from ..models import (
    Document,
    DocumentComment,
    DocumentFeedback,
    DocumentVersion,
)
from ..permissions import DocumentAccess


class DocumentSerializer(serializers.ModelSerializer):
    class DocumentNestedVersionSerializer(serializers.ModelSerializer):
        class Meta:
            model = DocumentVersion
            fields = ["id", "document", "number", "content", "status", "created_at"]
            read_only_fields = ["created_at"]

    class DocumentNestedFeedbackSerializer(serializers.ModelSerializer):
        class Meta:
            model = DocumentFeedback
            fields = ["id", "document", "version", "given_by", "decision", "created_at"]
            read_only_fields = ["created_at", "given_by"]

    class DocumentNestedCommentSerializer(serializers.ModelSerializer):
        class Meta:
            model = DocumentComment
            fields = ["id", "document", "version", "author", "content", "block_index", "quote", "created_at"]
            read_only_fields = ["created_at", "author"]

    versions = DocumentNestedVersionSerializer(many=True, read_only=True)
    feedbacks = DocumentNestedFeedbackSerializer(many=True, read_only=True)
    comments = DocumentNestedCommentSerializer(many=True, read_only=True)

    # Computed for the requesting user, so the frontend doesn't have to reimplement
    # the admin-override / guardian-permission logic to decide what UI to show.
    can_edit = serializers.SerializerMethodField()
    can_manage_sharing = serializers.SerializerMethodField()
    is_admin_view = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "task",
            "type",
            "author",
            "title",
            "icon",
            "cover",
            "cover_style",
            "cover_credit",
            "notes",
            "folder",
            "visibility",
            "allow_member_edit",
            "can_edit",
            "can_manage_sharing",
            "is_admin_view",
            "versions",
            "feedbacks",
            "comments",
            "deleted_at",
            "deleted_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "author", "deleted_at", "deleted_by"]

    access = DocumentAccess()

    def _request_user(self):
        request = self.context.get("request")
        return getattr(request, "user", None)

    def get_is_admin_view(self, obj: Document) -> bool:
        user = self._request_user()
        return bool(user) and self.access.is_workplace_admin(obj.workplace, user)

    def get_can_manage_sharing(self, obj: Document) -> bool:
        user = self._request_user()
        if not user:
            return False
        return obj.author_id == user.id or self.access.is_workplace_admin(obj.workplace, user)

    def get_can_edit(self, obj: Document) -> bool:
        user = self._request_user()
        return bool(user) and self.access.can_edit(user, obj)
