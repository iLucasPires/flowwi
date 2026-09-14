from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin

from ..models import DocumentFeedback
from ..permissions import DocumentAccess
from ..selectors import DocumentSelector
from ..serializers import DocumentFeedbackSerializer


@extend_schema(tags=["Document Feedbacks"])
class DocumentFeedbackViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = DocumentFeedback.objects.all()
    serializer_class = DocumentFeedbackSerializer
    permission_classes = [IsAuthenticated]
    workplace_lookup_field = "document__workplace"
    access = DocumentAccess()

    def get_queryset(self):
        workplace = self.get_workplace()
        if workplace is None:
            return self.queryset.none()
        return self.queryset.filter(document__in=DocumentSelector.viewable_for(workplace, self.request.user))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        document = serializer.validated_data["document"]
        version = serializer.validated_data.get("version")

        # Like comments, giving feedback (like/dislike) only requires view access.
        if not self.access.can_view(request.user, document):
            raise PermissionDenied("Você não tem acesso a este documento.")

        defaults = {k: v for k, v in serializer.validated_data.items() if k not in ("document", "version")}

        obj, _ = DocumentFeedback.objects.update_or_create(
            document=document,
            version=version,
            given_by=request.user,
            defaults=defaults,
        )

        return Response(
            data=self.get_serializer(obj).data,
            status=status.HTTP_200_OK,
        )
