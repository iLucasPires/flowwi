from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as s
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin
from apps.domains.workplace.permissions import IsDesignerOrReadOnly
from lib.paginations import LargeResultsSetPagination
from lib.utils.fractional_indexing import generate_key_between

from ..models import DocumentType
from ..serializers import DocumentTypeSerializer


@extend_schema(tags=["Document Types"])
class DocumentTypeViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer
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
            DocumentType.objects.filter(workplace=workplace)
            .exclude(position="")
            .order_by("-position")
            .values_list("position", flat=True)
            .first()
        )

        serializer.save(
            workplace=workplace,
            position=generate_key_between(last or None, None),
        )

    @extend_schema(
        request=inline_serializer("DocumentTypeReorderInput", fields={"position": s.CharField()}),
        responses={200: DocumentTypeSerializer},
    )
    @action(detail=True, methods=["post"], url_path="reorder")
    def reorder(self, request, pk=None):
        document_type = self.get_object()
        position = request.data.get("position")
        if not position:
            return Response({"position": ["This field is required."]}, status=400)
        document_type.position = position
        document_type.save(update_fields=["position", "updated_at"])
        return Response(DocumentTypeSerializer(document_type).data)
