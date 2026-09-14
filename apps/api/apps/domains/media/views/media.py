from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.streaming.views import sse_response
from apps.domains.media.agents.task import media_task_generator_agent
from apps.domains.workplace.mixins import WorkplaceViewSetMixin
from lib.renderers import SSERenderer

from ..models import Media, MediaComment
from ..realtime import media_channel_name
from ..serializers import MediaSerializer


@extend_schema(tags=["Media"])
class MediaViewSet(WorkplaceViewSetMixin, viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["task", "type"]
    workplace_lookup_field = "workplace"

    def perform_create(self, serializer):
        serializer.save(workplace=self.get_workplace(), designer=self.request.user)

    def get_queryset(self):
        workplace = self.get_workplace()
        if workplace is None:
            return self.queryset.none()
        return self.queryset.filter(workplace=workplace).prefetch_related(
            "versions__feedbacks",
            "versions__comments",
            "feedbacks",
            "comments",
        )

    @action(detail=True, methods=["post"], url_path="generate-task")
    def generate_task(self, request, pk=None):
        media = self.get_object()
        comment_ids = request.data.get("comment_ids", [])
        if not comment_ids:
            return Response(
                data={"comment_ids": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comments = MediaComment.objects.filter(media=media, pk__in=comment_ids)
        if not comments.exists():
            return Response(
                data={"comment_ids": ["Nenhum comentário válido encontrado."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        context = (request.data.get("context") or "").strip()

        feedback_lines = "\n".join(f"- {c.content}" for c in comments)
        prompt = (
            f"Media: {media.title or 'Sem título'}\n"
            f"Notas internas: {media.notes or '—'}\n\n"
            f"Comentários de feedback selecionados:\n{feedback_lines}"
        )
        if context:
            prompt += f"\n\nContexto extra fornecido pelo usuário:\n{context}"

        result = media_task_generator_agent.run_sync(prompt)
        return Response(result.output.model_dump())

    @extend_schema(
        summary="Stream de comentários (SSE)",
        description="Abre uma conexão Server-Sent Events para receber novos comentários da mídia em tempo real.",
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="sse",
        renderer_classes=[SSERenderer],
    )
    def sse(self, request, pk=None):
        media = self.get_object()

        return sse_response(media_channel_name(media.id))
