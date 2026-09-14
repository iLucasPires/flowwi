from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin

from ..models import DocumentComment, DocumentVersionStatus
from ..permissions import DocumentAccess
from ..selectors import DocumentSelector
from ..serializers import DocumentCommentSerializer


@extend_schema(tags=["Document Comments"])
class DocumentCommentViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = DocumentComment.objects.all()
    serializer_class = DocumentCommentSerializer
    permission_classes = [IsAuthenticated]
    workplace_lookup_field = "document__workplace"
    access = DocumentAccess()

    def get_queryset(self):
        workplace = self.get_workplace()
        if workplace is None:
            return self.queryset.none()

        # Confined to documents the user can actually view — otherwise a private
        # document's comments would leak through this endpoint even though the
        # document itself is hidden from them.
        return self.queryset.filter(document__in=DocumentSelector.viewable_for(workplace, self.request.user))

    def perform_create(self, serializer):
        document = serializer.validated_data["document"]
        if document.workplace_id != self.get_workplace().id:
            raise PermissionDenied("Document does not belong to this workplace.")

        # Commenting is a feedback action, open to anyone who can *view* the document —
        # not just those with edit access, same as media/task feedback elsewhere.
        if not self.access.can_view(self.request.user, document):
            raise PermissionDenied("Você não tem acesso a este documento.")

        # Comments always anchor to a version — general (non-anchored) comments fall
        # back to the document's latest version. Only a published version can be
        # commented on; drafts are still being written and shouldn't collect feedback yet.
        version = serializer.validated_data.get("version") or document.versions.first()

        if version is None or version.status != DocumentVersionStatus.PUBLISHED:
            raise PermissionDenied("Comments can only be added to a published version.")

        serializer.save(author=self.request.user, version=version)
