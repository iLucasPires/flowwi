from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.domains.inbox.models import InboxType
from apps.domains.inbox.services import InboxService

from ..mixins import WorkplaceViewSetMixin
from ..models import WorkplaceMember, WorkplaceMemberStatus
from ..permissions import IsWorkplaceAdminToManageMembers
from ..serializers import WorkplaceMemberSerializer


@extend_schema(tags=["Workplace Members"])
class WorkplaceMemberViewSet(
    WorkplaceViewSetMixin,
    viewsets.ModelViewSet,
):
    queryset = WorkplaceMember.objects.select_related("user").prefetch_related("user__profile")
    serializer_class = WorkplaceMemberSerializer
    permission_classes = [IsAuthenticated, IsWorkplaceAdminToManageMembers]
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

        queryset = self.queryset.filter(workplace=workplace)

        # The status filter only makes sense for the collection endpoint — detail
        # actions (retrieve/update/destroy/approve) must be able to find a member
        # regardless of status, e.g. approving or rejecting a pending request.
        if self.action != "list":
            return queryset

        status_param = self.request.query_params.get("status")
        if status_param == WorkplaceMemberStatus.PENDING:
            return queryset.filter(status=WorkplaceMemberStatus.PENDING)
        if status_param == "all":
            return queryset

        return queryset.filter(status=WorkplaceMemberStatus.ACTIVE)

    def perform_create(self, serializer):
        serializer.save(workplace=self.get_workplace())

    @action(detail=True, methods=["post"])
    def approve(self, request, public_id=None):
        member = self.get_object()
        member.status = WorkplaceMemberStatus.ACTIVE
        member.save(update_fields=["status"])

        InboxService().send_inbox(
            member=member,
            title="Pedido de entrada aprovado",
            message=f"Você foi aprovado no workspace {member.workplace.name}.",
            type=InboxType.MEMBER_JOINED,
        )

        return Response(self.get_serializer(member).data)
