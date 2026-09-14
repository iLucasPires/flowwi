from django.utils import timezone
from rest_framework import serializers

from apps.domains.workplace.serializers import WorkplaceMemberSerializer
from lib.serializers import ExpandableSerializerModel
from lib.utils.fractional_indexing import generate_key_between

from ..models import Task, TaskStatus, TaskStatusCategory, TaskType
from .status import TaskStatusSerializer
from .subtask import SubTaskSerializer
from .tag import TaskTagSerializer
from .type import TaskTypeSerializer


class TaskSerializer(ExpandableSerializerModel, serializers.ModelSerializer):
    expandable_fields = {
        "subs": lambda: SubTaskSerializer(many=True, read_only=True),
        "tags": lambda: TaskTagSerializer(many=True, read_only=True),
        "assignees": lambda: WorkplaceMemberSerializer(many=True, read_only=True),
        "type": lambda: TaskTypeSerializer(read_only=True),
        "status": lambda: TaskStatusSerializer(read_only=True),
    }

    class Meta:
        model = Task
        fields = [
            "id",
            "public_id",
            "workplace",
            "title",
            "description",
            "type",
            "status",
            "priority",
            "position",
            "origin",
            "deadline",
            "completed_at",
            "created_by",
            "assignees",
            "tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "workplace",
            "position",
            "created_at",
            "updated_at",
            "completed_at",
        ]

    def create(self, validated_data):
        workplace = validated_data.get("workplace")

        status = validated_data.get("status")
        if status is None:
            status = TaskStatus.objects.filter(workplace=workplace).order_by("position").first()
            validated_data["status"] = status

        if validated_data.get("type") is None:
            task_type = TaskType.objects.filter(workplace=workplace).order_by("position").first()
            validated_data["type"] = task_type

        last = (
            Task.objects.filter(status=status, workplace=workplace)
            .exclude(position="")
            .order_by("-position")
            .values_list("position", flat=True)
            .first()
        )

        validated_data["position"] = generate_key_between(last or None, None)

        if status is not None and status.category == TaskStatusCategory.DONE:
            validated_data["completed_at"] = timezone.now()

        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "status" in validated_data:
            new_status = validated_data["status"]
            was_done = instance.status is not None and instance.status.category == TaskStatusCategory.DONE
            is_done = new_status is not None and new_status.category == TaskStatusCategory.DONE

            if is_done and not was_done:
                validated_data["completed_at"] = timezone.now()
            elif not is_done and was_done:
                validated_data["completed_at"] = None

        return super().update(instance, validated_data)
