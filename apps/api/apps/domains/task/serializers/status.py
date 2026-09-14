from rest_framework import serializers

from ..models import TaskStatus


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatus
        fields = [
            "id",
            "name",
            "color",
            "icon",
            "category",
            "position",
            "workplace",
        ]
        read_only_fields = [
            "position",
            "workplace",
        ]
