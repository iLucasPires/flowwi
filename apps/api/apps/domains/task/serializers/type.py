from rest_framework import serializers

from ..models import TaskType


class TaskTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskType
        fields = [
            "id",
            "name",
            "color",
            "icon",
            "position",
            "workplace",
        ]
        read_only_fields = [
            "position",
            "workplace",
        ]
