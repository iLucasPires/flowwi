from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as s
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin
from apps.domains.workplace.permissions import IsDesignerOrReadOnly
from lib.utils.fractional_indexing import generate_key_between

from ..models import SubTask
from ..serializers import SubTaskSerializer


@extend_schema(tags=["Task Subs"])
class SubTaskViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    permission_classes = [IsAuthenticated, IsDesignerOrReadOnly]
    lookup_field = "public_id"
    workplace_lookup_field = "task__workplace"

    def get_queryset(self):
        return SubTask.objects.order_by("position")

    def perform_create(self, serializer):
        task = serializer.validated_data["task"]

        last = (
            SubTask.objects.filter(task=task)
            .exclude(position="")
            .order_by("-position")
            .values_list("position", flat=True)
            .first()
        )

        serializer.save(position=generate_key_between(last or None, None))

    @extend_schema(
        request=inline_serializer("SubReorderInput", fields={"position": s.CharField()}),
        responses={200: SubTaskSerializer},
    )
    @action(detail=True, methods=["post"], url_path="reorder")
    def reorder(self, request, public_id=None):
        sub = self.get_object()
        position = request.data.get("position")
        if not position:
            return Response({"position": ["This field is required."]}, status=400)
        sub.position = position
        sub.save(update_fields=["position", "updated_at"])
        return Response(SubTaskSerializer(sub).data)
