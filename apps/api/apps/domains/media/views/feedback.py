from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin

from ..models import MediaFeedback
from ..serializers import MediaFeedbackSerializer


@extend_schema(tags=["Media Feedbacks"])
class MediaFeedbackViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = MediaFeedback.objects.all()
    serializer_class = MediaFeedbackSerializer
    permission_classes = [IsAuthenticated]
    workplace_lookup_field = "media__workplace"

    def get_queryset(self):
        workplace = self.get_workplace()
        if workplace is None:
            return self.queryset.none()
        return self.queryset.filter(**{self.workplace_lookup_field: workplace})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        media = serializer.validated_data["media"]
        version = serializer.validated_data.get("version")

        defaults = {k: v for k, v in serializer.validated_data.items() if k not in ("media", "version")}

        obj, _ = MediaFeedback.objects.update_or_create(
            media=media,
            version=version,
            given_by=request.user,
            defaults=defaults,
        )

        return Response(
            data=self.get_serializer(obj).data,
            status=status.HTTP_200_OK,
        )
