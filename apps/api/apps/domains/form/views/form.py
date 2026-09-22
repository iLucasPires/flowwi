from django.db.models import Count
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.domains.form.agents.form import FormGeneratorDeps, form_generator_agent
from apps.domains.workplace.mixins import WorkplaceViewSetMixin

from ..models import Form
from ..serializers import FormPublicSerializer, FormResponseSerializer, FormSerializer
from ..services import FormService


@extend_schema(tags=["Forms"])
class FormViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["title", "description"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FormService()

    def get_queryset(self):
        qs = super().get_queryset().annotate(responses_count=Count("responses", distinct=True))
        workplace = self.get_workplace()

        if workplace:
            qs = qs.filter(workplace=workplace)

        return qs

    def perform_create(self, serializer):
        serializer.save(workplace=self.get_workplace())

    # -------------------------------------------------------------------------
    # Public actions
    # -------------------------------------------------------------------------

    @action(
        detail=False,
        methods=["get"],
        url_path="public/(?P<public_id>[^/.]+)",
        permission_classes=[AllowAny],
    )
    def public_detail(self, request: Request, public_id=None):
        # Drafts are visible here too, but only to an authenticated member of the form's
        # own workplace — this is what makes the editor's "Visualizar" work pre-publish.
        form = self.service.get_preview(public_id, request.user)
        if not form:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(FormPublicSerializer(form).data)

    @action(
        detail=False,
        methods=["post"],
        url_path="public/(?P<public_id>[^/.]+)/respond",
        permission_classes=[AllowAny],
    )
    def public_submit(self, request: Request, public_id=None):
        form = self._get_published_form(public_id)
        if not form:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if form.require_auth and not request.user.is_authenticated:
            return Response(
                {"detail": "Autenticação necessária."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        payload = self._build_response_payload(request, form)
        if isinstance(payload, Response):
            return payload

        serializer = FormResponseSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # -------------------------------------------------------------------------
    # Authenticated actions
    # -------------------------------------------------------------------------

    @action(detail=True, methods=["get"], url_path="insights")
    def insights(self, request: Request, pk=None):
        return Response(self.service.get_insights(self.get_object()))

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request: Request):
        prompt = (request.data.get("prompt") or "").strip()
        if not prompt:
            return Response(
                {"detail": "O campo 'prompt' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = form_generator_agent.run_sync(prompt, deps=FormGeneratorDeps())
        return Response(result.output.model_dump())

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _get_published_form(self, public_id: str) -> Form | None:
        return self.service.get_public_form(public_id)

    def _build_response_payload(self, request: Request, form: Form) -> dict | Response:
        payload = {
            "form": form.pk,
            "answers": request.data.get("answers", []),
        }

        if form.require_identity:
            respondent = self._extract_respondent(request)
            if not respondent:
                return Response(
                    {"detail": "Informe e-mail ou telefone."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            payload.update(respondent)

        return payload

    def _extract_respondent(self, request: Request) -> dict | None:
        email = request.data.get("respondent_email", "")
        phone = request.data.get("respondent_phone", "")

        if not email and request.user.is_authenticated:
            email = request.user.email

        if not email and not phone:
            return None

        return {"respondent_email": email, "respondent_phone": phone}
