from rest_framework import serializers

from apps.domains.workplace.serializers import WorkplaceMemberSerializer
from lib.serializers import ExpandableSerializerModel

from ..models import Inbox


class InboxSerializer(ExpandableSerializerModel, serializers.ModelSerializer):
    expandable_fields = {
        "sender": lambda: WorkplaceMemberSerializer(read_only=True),
    }

    related_member = serializers.SerializerMethodField()

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
            "related_member",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "related_member"]

    def get_related_member(self, obj: Inbox) -> dict | None:
        if obj.related_member_id is None:
            return None
        return {"public_id": obj.related_member.public_id, "status": obj.related_member.status}
