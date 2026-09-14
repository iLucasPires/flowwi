from django.db.models import QuerySet

from apps.domains.workplace.models import WorkplaceMember
from lib.bases import ServiceBase
from lib.utils import channel_name as build_channel_name

from ..models import Inbox


class InboxService(ServiceBase):
    def __init__(self):
        super().__init__(model=Inbox)

    @staticmethod
    def channel_name(member_id) -> str:
        """Single source of truth for the member's SSE channel name (see
        `apps.common.streaming`) — used by both the `sse` action and the `post_save`
        signal, so the two can never drift apart."""
        return build_channel_name("member", member_id)

    @staticmethod
    def build_inbox_payload(inbox: Inbox) -> dict:
        return {
            "id": str(inbox.id),
            "title": inbox.title,
            "message": inbox.message,
            "type": inbox.type,
            "is_read": inbox.is_read,
            "sender": inbox.sender_id,
            "created_at": inbox.created_at.isoformat() if inbox.created_at else None,
        }

    @staticmethod
    def mark_as_read(inbox: Inbox) -> None:
        inbox.is_read = True
        inbox.save(update_fields=["is_read"])

    @staticmethod
    def mark_all_as_read(queryset: QuerySet[Inbox]) -> None:
        queryset.filter(is_read=False).update(is_read=True)

    @staticmethod
    def delete_all(queryset: QuerySet[Inbox]) -> None:
        queryset.delete()

    def send_inbox(
        self,
        *,
        member: WorkplaceMember,
        title: str,
        message: str,
        type: int | None = None,
        sender: WorkplaceMember | None = None,
    ) -> Inbox:
        return self.create({"member": member, "title": title, "message": message, "type": type, "sender": sender})

    def send_bulk(
        self,
        *,
        members: list[WorkplaceMember],
        title: str,
        message: str,
        type: int | None = None,
        sender: WorkplaceMember | None = None,
    ) -> list[Inbox]:
        inboxes = [Inbox(member=m, title=title, message=message, type=type, sender=sender) for m in members]
        return self.bulk_create(inboxes)
