from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.domains.workplace.mixins import WorkplaceViewSetMixin
from apps.domains.workplace.permissions import IsDesignerOrReadOnly

from ..models import TaskTag
from ..serializers import TaskTagSerializer


@extend_schema(tags=["Task Tags"])
class TaskTagViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = TaskTag.objects.all()
    serializer_class = TaskTagSerializer
    permission_classes = [
        IsAuthenticated,
        IsDesignerOrReadOnly,
    ]
