from django.db.models import QuerySet

from apps.domains.workplace.models import WorkplaceMember
from lib.bases import ServiceBase

from ..models import Inbox


class InboxService(ServiceBase):
    def __init__(self):
        super().__init__(model=Inbox)

    @staticmethod
    def build_inbox_payload(inbox: Inbox) -> dict:
        return {
            "id": str(inbox.id),
            "title": inbox.title,
            "message": inbox.message,
            "type": inbox.type,
            "is_read": inbox.is_read,
            "sender": inbox.sender_id,
            "related_member": InboxService._related_member_payload(inbox),
            "created_at": inbox.created_at.isoformat() if inbox.created_at else None,
        }

    @staticmethod
    def _related_member_payload(inbox: Inbox) -> dict | None:
        if inbox.related_member_id is None:
            return None
        return {"public_id": str(inbox.related_member.public_id), "status": inbox.related_member.status}

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
        related_member: WorkplaceMember | None = None,
    ) -> Inbox:
        return self.create(
            {
                "member": member,
                "title": title,
                "message": message,
                "type": type,
                "sender": sender,
                "related_member": related_member,
            }
        )

    def send_bulk(
        self,
        *,
        members: list[WorkplaceMember],
        title: str,
        message: str,
        type: int | None = None,
        sender: WorkplaceMember | None = None,
        related_member: WorkplaceMember | None = None,
    ) -> list[Inbox]:
        inboxes = [
            Inbox(member=m, title=title, message=message, type=type, sender=sender, related_member=related_member)
            for m in members
        ]
        return self.bulk_create(inboxes)
