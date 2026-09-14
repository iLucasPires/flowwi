from rest_framework import serializers

from ..models import MediaComment


class MediaCommentSerializer(serializers.ModelSerializer):
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
        # `guest_name` is set server-side only, from the public share-link flow
        # (`apps.media.views.public.MediaPublicCommentView`) — never through this
        # serializer's own `create`/`update`.
        read_only_fields = ["created_at", "author", "guest_name"]
