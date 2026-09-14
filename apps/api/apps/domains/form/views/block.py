from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin

from ..models import Form, FormBlock
from ..serializers import FormBlockSerializer
from ..services import FormBlockService


@extend_schema(tags=["Form Blocks"])
class FormBlockViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = FormBlock.objects.select_related("page")
    serializer_class = FormBlockSerializer
    permission_classes = [IsAuthenticated]
    workplace_lookup_field = "form__workplace"
    # The editor always needs every block for a form in one shot to rebuild the document —
    # the default DRF pagination (PAGE_SIZE=10) was silently truncating any form past 10
    # blocks, which the frontend has no way to detect (it just renders what it got).
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        workplace = self.get_workplace()

        if workplace:
            qs = qs.filter(form__workplace=workplace)

        form_id = self.request.query_params.get("form")

        if form_id:
            qs = qs.filter(form_id=form_id)

        return qs

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk_save(self, request: Request):
        pages, blocks = self._split_payload(request.data)

        form = self._get_form(blocks)
        if not form:
            return Response(status=status.HTTP_404_NOT_FOUND)

        service = FormBlockService()
        should_sync = pages or self._has_page_ordering(blocks)

        saved = service.bulk_sync(form, pages, blocks) if should_sync else service.bulk_upsert(form, blocks)

        return Response(
            FormBlockSerializer(saved, many=True).data,
            status=status.HTTP_201_CREATED,
        )

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _split_payload(self, body) -> tuple[list, list]:
        """Split request body into (pages, blocks)."""
        if isinstance(body, list):
            return [], body

        return body.get("pages") or [], body.get("blocks") or []

    def _get_form(self, raw_blocks: list) -> Form | None:
        """Resolve form from URL kwargs or first block's form field."""
        form_id = self.kwargs.get("form_pk")

        if not form_id and raw_blocks and isinstance(raw_blocks[0], dict):
            form_id = raw_blocks[0].get("form")

        if not form_id:
            return None

        return Form.objects.filter(id=form_id, workplace=self.get_workplace()).first()

    def _has_page_ordering(self, blocks: list) -> bool:
        return any(isinstance(b, dict) and "page_order" in b for b in blocks)
