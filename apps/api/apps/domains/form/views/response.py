from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin

from ..models import FormResponse
from ..serializers import FormResponseSerializer


@extend_schema(tags=["Form Responses"])
class FormResponseViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = FormResponse.objects.all()
    serializer_class = FormResponseSerializer
    permission_classes = [IsAuthenticated]
    workplace_lookup_field = "form__workplace"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("form").prefetch_related("answers").order_by("-created_at")

        if workplace := self.get_workplace():
            queryset = queryset.filter(form__workplace=workplace)

        return queryset
