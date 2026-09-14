from rest_framework import serializers

from apps.domains.workplace.serializers import WorkplaceMemberSerializer
from lib.serializers import ExpandableSerializerModel

from ..models import Inbox


class InboxSerializer(ExpandableSerializerModel, serializers.ModelSerializer):
    expandable_fields = {
        "sender": lambda: WorkplaceMemberSerializer(read_only=True),
    }

    class Meta:
        model = Inbox
        fields = [
            "id",
            "public_id",
            "member",
            "sender",
            "type",
            "title",
            "message",
            "is_read",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
