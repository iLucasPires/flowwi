from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin

from ..agents.theme import ThemeGeneratorDeps, theme_generator_agent
from ..models import FormTheme
from ..selectors import FormThemeSelector
from ..serializers import FormThemeSerializer
from ..services import FormThemeService


@extend_schema(tags=["Form Themes"])
class FormThemeViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = FormTheme.objects.all()
    serializer_class = FormThemeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FormThemeService()

    def get_queryset(self):
        return FormThemeSelector.for_workplace(self.get_workplace())

    def perform_create(self, serializer):
        serializer.save(workplace=self.get_workplace(), is_preset=False)

    def perform_update(self, serializer):
        if serializer.instance.is_preset:
            raise PermissionDenied("Presets não podem ser editados — duplique para customizar.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.is_preset:
            raise PermissionDenied("Presets não podem ser removidos.")
        instance.delete()

    @action(detail=True, methods=["post"], url_path="duplicate")
    def duplicate(self, request: Request, pk=None):
        theme = self.get_object()
        copy = self.service.duplicate(theme, self.get_workplace())
        return Response(FormThemeSerializer(copy).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request: Request):
        prompt = (request.data.get("prompt") or "").strip()
        if not prompt:
            return Response(
                {"detail": "O campo 'prompt' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = theme_generator_agent.run_sync(prompt, deps=ThemeGeneratorDeps())
        return Response(result.output.model_dump())
