"""Google Drive file operation views."""

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.domains.workplace.mixins import WorkplaceViewSetMixin

from ..models import GoogleDriveConnection
from ..serializers import GoogleDriveConnectionSerializer
from ..services.google import GoogleDriveService


@extend_schema(tags=["Google Drive"])
class GoogleDriveViewSet(WorkplaceViewSetMixin, viewsets.GenericViewSet):
    queryset = GoogleDriveConnection.objects.all()
    serializer_class = GoogleDriveConnectionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["get"], url_path="files")
    def list_files(self, request, pk=None):
        connection = self.get_object()
        service = GoogleDriveService()
        files = service.list_files(connection)

        return Response({"files": files})
