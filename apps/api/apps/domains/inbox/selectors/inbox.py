from django.db.models import QuerySet

from apps.domains.workplace.models import WorkplaceMember

from ..models import Inbox


class InboxSelector:
    @staticmethod
    def for_member(member: WorkplaceMember) -> QuerySet[Inbox]:
        return Inbox.objects.filter(member=member).select_related("related_member").order_by("-created_at")
