from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..mixins import WorkplaceViewSetMixin
from ..models import WorkplaceMember
from ..serializers import WorkplaceMemberSerializer


@extend_schema(tags=["Workplace Members"])
class WorkplaceMemberViewSet(
    WorkplaceViewSetMixin,
    viewsets.ModelViewSet,
):
    queryset = WorkplaceMember.objects.select_related("user").prefetch_related("user__profile")
    serializer_class = WorkplaceMemberSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "public_id"
    require_workplace = True
    search_fields = [
        "user__username",
        "user__email",
        "user__profile__full_name",
    ]

    def get_queryset(self):
        workplace = self.get_workplace()

        if workplace is None:
            return self.queryset.none()

        return self.queryset.filter(workplace=workplace)

    def perform_create(self, serializer):
        serializer.save(workplace=self.get_workplace())
