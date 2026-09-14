from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin

from ..models import Document, DocumentVersion
from ..permissions import DocumentAccess, DocumentRelatedObjectPermission
from ..realtime import notify_document_changed
from ..selectors import DocumentSelector
from ..serializers import DocumentVersionSerializer
from ..services import DocumentVersionService


@extend_schema(tags=["Document Versions"])
class DocumentVersionViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = DocumentVersion.objects.all()
    serializer_class = DocumentVersionSerializer
    # A version's content IS the document's content — reading/writing it follows the
    # same view_document/change_document guardian grant as the document itself
    # (resolved against `version.document`), not just workplace membership.
    permission_classes = [IsAuthenticated, DocumentRelatedObjectPermission]
    workplace_lookup_field = "document__workplace"
    access = DocumentAccess()

    def get_queryset(self):
        workplace = self.get_workplace()
        if workplace is None:
            return self.queryset.none()

        return self.queryset.filter(document__in=DocumentSelector.viewable_for(workplace, self.request.user))

    def create(self, request, *args, **kwargs):
        service = DocumentVersionService()
        document_id = request.data.get("document")

        if not document_id:
            return Response(
                data={"document": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            document = Document.objects.get(
                pk=document_id,
                workplace=self.get_workplace(),
            )
        except Document.DoesNotExist:
            return Response(
                data={"document": ["Document not found."]},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not self.access.can_edit(request.user, document):
            raise PermissionDenied("Você não tem permissão para editar este documento.")

        version = service.add_version(
            document.id,
            content=request.data.get("content"),
        )

        notify_document_changed(document.id)

        return Response(
            data=self.get_serializer(version).data,
            status=status.HTTP_201_CREATED,
        )

    def perform_update(self, serializer):
        # Plain content autosaves happen every ~900ms while someone types — the lock
        # already keeps everyone else read-only during that, so broadcasting on every
        # keystroke would just spam other tabs with refetches for no benefit. Only
        # `status` changes (draft ↔ published) actually change what others should see.
        notify_others = "status" in serializer.validated_data
        serializer.save()
        if notify_others:
            notify_document_changed(serializer.instance.document_id)

    @action(detail=True, methods=["post"], url_path="new-revision")
    def new_revision(self, request, pk=None):
        version = self.get_object()
        service = DocumentVersionService()

        new_version = service.new_revision(version.id)

        notify_document_changed(version.document_id)

        return Response(
            data=self.get_serializer(new_version).data,
            status=status.HTTP_201_CREATED,
        )
