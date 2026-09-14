from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin
from apps.integrations.google.models import GoogleDriveConnection
from apps.integrations.google.services.google import GoogleDriveService

from ..models import Media, MediaVersion, MediaVersionType
from ..serializers import MediaVersionSerializer
from ..utils import get_media_version_type_by_file_name


@extend_schema(tags=["Media Versions"])
class MediaVersionViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = MediaVersion.objects.all()
    serializer_class = MediaVersionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["media", "type"]
    workplace_lookup_field = "media__workplace"

    def get_queryset(self):
        workplace = self.get_workplace()
        if workplace is None:
            return self.queryset.none()
        return self.queryset.filter(**{self.workplace_lookup_field: workplace})

    def create(self, request, *args, **kwargs):
        media_id = request.data.get("media")
        file = request.FILES.get("file")
        text_content = (request.data.get("text_content") or "").strip()

        if not media_id:
            return Response(
                data={"detail": "media is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            media = Media.objects.select_related("workplace").get(pk=media_id, workplace=self.get_workplace())
        except Media.DoesNotExist:
            return Response(
                data={"detail": "Media not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        next_v = (MediaVersion.objects.filter(media=media).aggregate(max_v=models.Max("number"))["max_v"] or 0) + 1

        if text_content and not file:
            version = MediaVersion.objects.create(
                media=media,
                number=next_v,
                type=MediaVersionType.TEXT,
                text_content=text_content,
            )
            serializer = self.get_serializer(version)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        if not file:
            return Response(
                data={"detail": "media and file are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        workplace = self.get_workplace()

        connection = GoogleDriveConnection.objects.filter(
            workplace=workplace,
            is_active=True,
        ).first()

        if not connection:
            return Response(
                data={"detail": "No active Google Drive connection for this workplace."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Upload to Google Drive
        service = GoogleDriveService()

        drive_data = service.upload_file(
            connection=connection,
            file_content=file.read(),
            file_name=file.name,
            mime_type=file.content_type or "application/octet-stream",
        )

        # Create version
        version = MediaVersion.objects.create(
            media=media,
            number=next_v,
            type=get_media_version_type_by_file_name(file.name),
            drive_file_id=drive_data["file_id"],
            drive_url=drive_data["web_view_link"],
            file_name=drive_data["name"],
            mime_type=drive_data["mime_type"],
        )

        serializer = self.get_serializer(version)

        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )
