from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin

from ..models import FormPage
from ..serializers import FormPageSerializer


@extend_schema(tags=["Form Pages"])
class FormPageViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = FormPage.objects.select_related("form")
    serializer_class = FormPageSerializer
    permission_classes = [IsAuthenticated]
    workplace_lookup_field = "form__workplace"
    # Same reasoning as FormBlockViewSet: the editor needs every page for a form at once.
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
