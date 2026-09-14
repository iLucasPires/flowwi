from rest_framework import serializers

from apps.domains.user.serializers import ProfileSerializer
from lib.serializers import ExpandableSerializerModel

from ..models import WorkplaceMember


class WorkplaceMemberSerializer(ExpandableSerializerModel, serializers.ModelSerializer):
    expandable_fields = {
        "profile": lambda: ProfileSerializer(source="user.profile", read_only=True),
    }

    class Meta:
        model = WorkplaceMember
        fields = [
            "id",
            "public_id",
            "workplace",
            "user",
            "role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
        ]
