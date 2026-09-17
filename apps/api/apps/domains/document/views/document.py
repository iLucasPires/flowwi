from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin

from ..agents.assist import AI_ASSIST_INSTRUCTIONS, document_assist_agent
from ..agents.task import document_task_generator_agent
from ..models import Document, DocumentComment
from ..permissions import DocumentAccess, DocumentObjectPermission
from ..realtime import notify_document_changed
from ..selectors import DocumentSelector
from ..serializers import DocumentSerializer
from ..services import DocumentService

# Changing who can see/edit a document is a sharing decision, not a content edit —
# reserved for the author and workplace admins even when a member has edit access.
SHARING_FIELDS = {"visibility", "allow_member_edit"}


@extend_schema(tags=["Documents"])
class DocumentViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated, DocumentObjectPermission]
    workplace_lookup_field = "workplace"
    access = DocumentAccess()

    def get_queryset(self):
        workplace = self.get_workplace()

        if workplace is None:
            return self.queryset.none()

        trashed = self.request.query_params.get("trashed", "").lower() == "true"

        base = self.queryset.filter(workplace=workplace, deleted_at__isnull=not trashed).prefetch_related(
            "versions",
            "feedbacks",
            "comments",
        )

        # Admins see every document, unfiltered — sharing settings only ever narrow
        # what *other* members get. Everyone else only sees what django-guardian
        # actually granted them (author's own docs, plus workplace-shared ones);
        # anything else 404s rather than 403s, so private docs don't leak existence.
        if self.access.is_workplace_admin(workplace, self.request.user):
            return base

        return DocumentSelector.viewable_for(workplace, self.request.user, trashed=trashed)

    def perform_create(self, serializer):
        serializer.save(
            workplace=self.get_workplace(),
            author=self.request.user,
        )

    def perform_destroy(self, instance):
        DocumentService().trash(instance, deleted_by=self.request.user)

    @extend_schema(responses={200: DocumentSerializer})
    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        document = get_object_or_404(
            Document,
            pk=pk,
            workplace=self.get_workplace(),
            deleted_at__isnull=False,
        )
        self.check_object_permissions(request, document)
        document = DocumentService().restore(document)
        return Response(DocumentSerializer(document, context={"request": request}).data)

    def perform_update(self, serializer):
        instance = serializer.instance
        user = self.request.user

        changing_sharing = SHARING_FIELDS & set(serializer.validated_data)

        if changing_sharing and not (
            instance.author_id == user.id or self.access.is_workplace_admin(instance.workplace, user)
        ):
            raise PermissionDenied("Apenas o autor ou administradores do workplace podem alterar o compartilhamento.")

        serializer.save()
        notify_document_changed(instance.id)

    @action(detail=True, methods=["post"], url_path="generate-task")
    def generate_task(self, request, pk=None):
        document = self.get_object()
        comment_ids = request.data.get("comment_ids", [])
        if not comment_ids:
            return Response(
                data={"comment_ids": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comments = DocumentComment.objects.filter(
            document=document,
            pk__in=comment_ids,
        )

        if not comments.exists():
            return Response(
                data={"comment_ids": ["Nenhum comentário válido encontrado."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        context = (request.data.get("context") or "").strip()

        feedback_lines = "\n".join(f"- {c.content}" for c in comments)

        prompt = (
            f"Document: {document.title or 'Sem título'}\n"
            f"Notas internas: {document.notes or '—'}\n\n"
            f"Comentários de feedback selecionados:\n{feedback_lines}"
        )

        if context:
            prompt += f"\n\nContexto extra fornecido pelo usuário:\n{context}"

        result = document_task_generator_agent.run_sync(prompt)
        return Response(data=result.output.model_dump())

    @action(detail=True, methods=["post"], url_path="ai-assist")
    def ai_assist(self, request, pk=None):
        document = self.get_object()

        action_key = (request.data.get("action") or "").strip()
        custom_prompt = (request.data.get("prompt") or "").strip()

        if not action_key and not custom_prompt:
            return Response(
                data={"prompt": ["Either action or prompt is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        latest_version = document.versions.order_by("-number").first()
        content = latest_version.content if latest_version and isinstance(latest_version.content, str) else ""

        instruction = AI_ASSIST_INSTRUCTIONS.get(action_key, "")
        prompt = f"Documento: {document.title or 'Sem título'}\n\nConteúdo atual:\n{content}\n\n"

        if instruction:
            prompt += f"Instrução: {instruction}"

        if custom_prompt:
            prompt += f"\n\nPedido do usuário: {custom_prompt}"

        result = document_assist_agent.run_sync(prompt)

        return Response(data={"output": result.output})
