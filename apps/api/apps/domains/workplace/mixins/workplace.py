from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.viewsets import GenericViewSet

from ..constants import WORKPLACE_COOKIE_NAME
from ..services import WorkplaceService


class WorkplaceViewSetMixin(GenericViewSet):
    workplace_lookup_field = "workplace"
    require_workplace = False

    def get_workplace_id(self):
        return self.request.COOKIES.get(WORKPLACE_COOKIE_NAME) or self.request.query_params.get("workplace_id")

    def get_workplace(self):
        if hasattr(self, "_workplace"):
            return self._workplace

        workplace_id = self.get_workplace_id()

        if not workplace_id:
            if self.require_workplace:
                raise NotFound("Workplace is required.")

            self._workplace = None
            return None

        workplace = WorkplaceService().get_or_none(pk=workplace_id)

        if not workplace:
            raise NotFound("Workplace not found.")

        self.validate_workplace_permission(workplace)

        self._workplace = workplace
        return workplace

    def validate_workplace_permission(self, workplace):
        if not workplace.members.filter(user=self.request.user).exists():
            raise PermissionDenied("You are not a member of this workplace.")
