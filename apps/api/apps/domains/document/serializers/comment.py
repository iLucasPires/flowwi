from rest_framework import serializers

from ..models import DocumentComment


class DocumentCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentComment
        fields = ["id", "document", "version", "author", "content", "block_index", "quote", "created_at"]
        read_only_fields = ["created_at", "author"]
