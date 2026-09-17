from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin
from lib.paginations import LargeResultsSetPagination

from ..models import QuickLink
from ..serializers import QuickLinkSerializer


@extend_schema(tags=["Quicklinks"])
class QuickLinkViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = QuickLink.objects.all()
    serializer_class = QuickLinkSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        workplace = self.get_workplace()
        if workplace is None:
            return self.queryset.none()
        return self.queryset.filter(workplace=workplace).select_related("created_by")

    def perform_create(self, serializer):
        workplace = self.get_workplace()
        member = workplace.members.get(user=self.request.user)
        serializer.save(workplace=workplace, created_by=member)
