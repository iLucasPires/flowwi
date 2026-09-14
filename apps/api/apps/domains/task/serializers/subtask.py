from rest_framework import serializers

from ..models import SubTask


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = [
            "id",
            "public_id",
            "task",
            "title",
            "is_done",
            "position",
            "assignee",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "position",
            "created_at",
            "updated_at",
        ]
