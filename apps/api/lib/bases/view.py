from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class ViewSetBase(viewsets.ModelViewSet):
    """
    Base viewset with multi-tenancy and optional nested resource support.

    Subclasses set:
        parent_lookup_field: URL kwarg name (e.g. "form_pk")
        parent_filter_field: queryset filter (e.g. "form_id")
    """

    permission_classes = [IsAuthenticated]
    parent_lookup_field: str | None = None
    parent_filter_field: str | None = None

    def get_queryset(self):
        qs = super().get_queryset()
        parent_pk = self._get_parent_pk()

        if parent_pk:
            qs = qs.filter(**{self.parent_filter_field: parent_pk})

        return qs

    def perform_create(self, serializer):
        parent_pk = self._get_parent_pk()
        if parent_pk:
            serializer.save(**{self.parent_filter_field: parent_pk})
        else:
            super().perform_create(serializer)

    def _get_parent_pk(self):
        if self.parent_lookup_field:
            return self.kwargs.get(self.parent_lookup_field)
        return None
