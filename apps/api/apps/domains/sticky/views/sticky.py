from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as s
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.domains.workplace.mixins import WorkplaceViewSetMixin
from lib.paginations import LargeResultsSetPagination
from lib.utils.fractional_indexing import generate_key_between

from ..models.sticky import Sticky
from ..permissions import StickyPermission
from ..selectors.sticky import StickySelector
from ..serializers.sticky import StickySerializer
from ..services.sticky import StickyService

# Same reasoning as Document's SHARING_FIELDS: who can see a sticky is a sharing
# decision, reserved for its creator and workplace admins, even though anyone with
# access to the sticky can otherwise edit its text/color freely.
VISIBILITY_FIELDS = {"visibility"}


@extend_schema(tags=["Stickies"])
class StickyViewSet(WorkplaceViewSetMixin, viewsets.ModelViewSet):
    queryset = Sticky.objects.all()
    serializer_class = StickySerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [IsAuthenticated, StickyPermission]
    ordering_fields = ["created_at", "updated_at", "position"]

    def get_queryset(self):
        user = self.request.user
        workplace = self.get_workplace()

        if workplace is None:
            return self.queryset.none()

        trashed = self.request.query_params.get("trashed", "").lower() == "true"

        return StickySelector.for_user(
            workplace=workplace,
            user=user,
            trashed=trashed,
        ).order_by("position", "-created_at")

    def perform_create(self, serializer):
        workplace = self.get_workplace()

        last = (
            Sticky.objects.filter(workplace=workplace)
            .exclude(position="")
            .order_by("-position")
            .values_list("position", flat=True)
            .first()
        )

        serializer.save(
            workplace=workplace,
            created_by=self.request.user,
            position=generate_key_between(last or None, None),
        )

    def perform_update(self, serializer):
        instance = serializer.instance
        user = self.request.user

        changing_visibility = VISIBILITY_FIELDS & set(serializer.validated_data)

        if changing_visibility and not (
            instance.created_by_id == user.id
            or instance.workplace.is_owner(user)
            or instance.workplace.is_manager(user)
        ):
            raise PermissionDenied(
                "Apenas quem criou o sticky ou administradores do workplace podem alterar a visibilidade."
            )

        serializer.save()

    def perform_destroy(self, instance):
        StickyService().trash(instance, deleted_by=self.request.user)

    @extend_schema(responses={200: StickySerializer})
    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        sticky = get_object_or_404(
            StickySelector.for_user(
                workplace=self.get_workplace(),
                user=request.user,
                trashed=True,
            ),
            pk=pk,
        )

        self.check_object_permissions(request, sticky)

        sticky = StickyService().restore(sticky)
        data = StickySerializer(sticky, context={"request": request}).data

        return Response(data)

    @extend_schema(
        request=inline_serializer(
            "StickyReorderInput",
            fields={"position": s.CharField()},
        ),
        responses={200: StickySerializer},
    )
    @action(detail=True, methods=["post"], url_path="reorder")
    def reorder(self, request, pk=None):
        sticky = self.get_object()
        position = request.data.get("position")
        if not position:
            return Response(
                data={"position": ["This field is required."]},
                status=400,
            )

        sticky.position = position
        sticky.save(update_fields=["position", "updated_at"])
        data = StickySerializer(sticky).data

        return Response(data)
