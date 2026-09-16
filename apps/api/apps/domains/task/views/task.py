from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin
from apps.domains.workplace.permissions import IsDesignerOrReadOnly

from ..models import Task, TaskStatus, TaskStatusCategory
from ..serializers import TaskSerializer
from ..services import TaskService


@extend_schema(tags=["Tasks"])
class TaskViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsDesignerOrReadOnly]
    lookup_field = "public_id"

    search_fields = ["title", "description"]
    ordering_fields = ["position", "title", "deadline", "created_at", "priority"]

    def get_queryset(self):
        workplace = self.get_workplace()
        if workplace is None:
            return Task.objects.none()

        trashed = self.request.query_params.get("trashed", "").lower() == "true"
        return (
            Task.objects.filter(workplace=workplace, deleted_at__isnull=not trashed)
            .select_related("created_by", "workplace", "status", "type")
            .prefetch_related("assignees", "tags")
            .order_by("status", "position")
        )

    def perform_create(self, serializer):
        serializer.save(workplace=self.get_workplace())

    def perform_destroy(self, instance):
        TaskService().trash(instance, deleted_by=self.request.user)

    @extend_schema(responses={200: TaskSerializer})
    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, public_id=None):
        task = get_object_or_404(
            Task,
            public_id=public_id,
            workplace=self.get_workplace(),
            deleted_at__isnull=False,
        )
        self.check_object_permissions(request, task)
        task = TaskService().restore(task)
        return Response(TaskSerializer(task, context={"request": request}).data)

    @extend_schema(
        request=inline_serializer(
            name="ReorderInput",
            fields={
                "position": serializers.CharField(),
                "status": serializers.CharField(required=False),
            },
        ),
        responses={200: TaskSerializer},
    )
    @action(detail=True, methods=["post"], url_path="reorder")
    def reorder(self, request, public_id=None):
        task = self.get_object()
        position = request.data.get("position")
        if not position:
            return Response({"position": ["This field is required."]}, status=400)
        task.position = position

        update_fields = ["position", "updated_at"]

        if "status" in request.data:
            was_done = task.status is not None and task.status.category == TaskStatusCategory.DONE
            new_status = TaskStatus.objects.filter(pk=request.data["status"]).first()
            task.status = new_status
            update_fields.append("status")

            is_done = new_status is not None and new_status.category == TaskStatusCategory.DONE

            if is_done and not was_done:
                task.completed_at = timezone.now()
                update_fields.append("completed_at")
            elif not is_done and was_done:
                task.completed_at = None
                update_fields.append("completed_at")

        task.save(update_fields=update_fields)
        serializer = self.get_serializer(task)

        return Response(serializer.data)
