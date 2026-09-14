from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as s
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin
from apps.domains.workplace.permissions import IsDesignerOrReadOnly
from lib.paginations import LargeResultsSetPagination
from lib.utils.fractional_indexing import generate_key_between

from ..models import TaskType
from ..serializers import TaskTypeSerializer


@extend_schema(tags=["Task Types"])
class TaskTypeViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = TaskType.objects.all()
    serializer_class = TaskTypeSerializer
    permission_classes = [IsAuthenticated, IsDesignerOrReadOnly]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        workplace = self.get_workplace()
        if workplace is None:
            return self.queryset.none()
        return self.queryset.filter(workplace=workplace).order_by("position")

    def perform_create(self, serializer):
        workplace = self.get_workplace()

        last = (
            TaskType.objects.filter(workplace=workplace)
            .exclude(position="")
            .order_by("-position")
            .values_list("position", flat=True)
            .first()
        )

        serializer.save(
            workplace=workplace,
            position=generate_key_between(last or None, None),
        )

    def perform_destroy(self, instance):
        if instance.tasks.exists():
            raise ValidationError({"detail": "Não é possível excluir: existem tarefas usando este tipo."})
        instance.delete()

    @extend_schema(
        request=inline_serializer("TaskTypeReorderInput", fields={"position": s.CharField()}),
        responses={200: TaskTypeSerializer},
    )
    @action(detail=True, methods=["post"], url_path="reorder")
    def reorder(self, request, pk=None):
        task_type = self.get_object()
        position = request.data.get("position")
        if not position:
            return Response({"position": ["This field is required."]}, status=400)
        task_type.position = position
        task_type.save(update_fields=["position", "updated_at"])
        return Response(TaskTypeSerializer(task_type).data)
