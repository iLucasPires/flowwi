from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..constants import WORKPLACE_COOKIE_NAME
from ..models import Workplace
from ..serializers import WorkplaceSerializer
from ..services import WorkplaceService


@extend_schema(tags=["Workplaces"])
class WorkplaceViewSet(viewsets.ModelViewSet):
    queryset = Workplace.objects.filter(deleted_at__isnull=True)

    serializer_class = WorkplaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return self.queryset.filter(members__user=user, members__status="active").distinct()

    def perform_destroy(self, instance):
        if not instance.is_owner(self.request.user):
            raise PermissionDenied("Apenas o owner pode excluir o workspace.")

        WorkplaceService().trash(instance)

    @action(detail=True, methods=["post"], url_path="select")
    def select(self, request, pk=None):
        workplace = self.get_object()
        response = Response(
            status=status.HTTP_200_OK,
            data=WorkplaceSerializer(
                workplace,
                context={"request": request},
            ).data,
        )
        response.set_cookie(
            key=WORKPLACE_COOKIE_NAME,
            value=str(workplace.pk),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            path="/",
        )
        return response

    @action(detail=False, methods=["post"], url_path="deselect")
    def deselect(self, request):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(WORKPLACE_COOKIE_NAME, path="/")
        return response

    @action(
        detail=False,
        methods=["post"],
        url_path="join",
    )
    def join(self, request):
        member = WorkplaceService().join_workplace(
            user=request.user,
            invite_key=request.data.get("invite_key", ""),
        )

        return Response(
            status=status.HTTP_200_OK,
            data={
                "status": member.status,
                "workplace": WorkplaceSerializer(
                    member.workplace,
                    context={"request": request},
                ).data,
            },
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="regenerate-invite-key",
    )
    def regenerate_invite_key(self, request, pk=None):
        workplace = WorkplaceService.regenerate_invite(self.get_object())

        return Response(
            data=WorkplaceSerializer(
                workplace,
                context={"request": request},
            ).data,
        )
