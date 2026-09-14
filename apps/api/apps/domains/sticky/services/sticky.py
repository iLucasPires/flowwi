from django.utils import timezone

from lib.bases import ServiceBase

from ..models.sticky import Sticky


class StickyService(ServiceBase):
    def __init__(self):
        super().__init__(Sticky)

    def trash(self, sticky: Sticky, *, deleted_by=None) -> Sticky:
        sticky.deleted_at = timezone.now()
        sticky.save(update_fields=["deleted_at", "updated_at"])
        
        return sticky

    def restore(self, sticky: Sticky) -> Sticky:
        sticky.deleted_at = None
        sticky.save(update_fields=["deleted_at", "updated_at"])

        return sticky

    def purge(self, sticky: Sticky) -> None:
        sticky.delete()
