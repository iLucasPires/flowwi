from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.streaming.views import sse_response
from apps.domains.workplace.mixins import WorkplaceViewSetMixin
from lib.paginations import LargeResultsSetPagination
from lib.renderers import SSERenderer
from lib.utils import channel_name

from ..models import Inbox
from ..selectors import InboxSelector
from ..serializers import InboxSerializer
from ..services import InboxService

inbox_service = InboxService()


@extend_schema(tags=["Inbox"])
class InboxViewSet(
    WorkplaceViewSetMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = InboxSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Inbox.objects.none()
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["type", "is_read"]
    require_workplace = True

    def get_member(self):
        if hasattr(self, "_member"):
            return self._member

        workplace = self.get_workplace()
        self._member = workplace.members.get(user=self.request.user)

        return self._member

    def get_queryset(self):
        return InboxSelector.for_member(self.get_member())

    @extend_schema(
        description="Mark a message as read",
        request=None,
        responses={204: None},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="read",
    )
    def read(self, request, pk=None):
        inbox_service.mark_as_read(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        description="Mark all messages as read",
        request=None,
        responses={204: None},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="read-all",
    )
    def read_all(self, request):
        inbox_service.mark_all_as_read(self.get_queryset())
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        description="Delete all messages",
        request=None,
        responses={204: None},
    )
    @action(
        detail=False,
        methods=["delete"],
        url_path="delete-all",
    )
    def destroy_all(self, request):
        inbox_service.delete_all(self.get_queryset())
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Stream de notificações (SSE)",
        description="Abre uma conexão Server-Sent Events para receber notificações em tempo real.",
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="sse",
        renderer_classes=[SSERenderer],
    )
    def sse(self, request):
        # Keyed by the stable User.id, not the active WorkplaceMember.id, so the
        # connection keeps receiving notifications even if the user switches their
        # active workplace mid-session — see `apps.domains.inbox.signals`.
        return sse_response(channel_name("user", request.user.id))
