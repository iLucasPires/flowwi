from django.contrib.auth import get_user_model

from apps.domains.inbox.models import InboxType
from apps.domains.inbox.services import InboxService
from lib.bases import ServiceBase

from ..exceptions import WorkplaceNotFound
from ..models import Workplace, WorkplaceMember, WorkplaceMemberRole, WorkplaceMemberStatus
from ..utils import generate_invite_key
from .member import WorkplaceMemberService

User = get_user_model()


class WorkplaceService(ServiceBase):
    """
    Workplace service class.
    """

    def __init__(self):
        super().__init__(Workplace)

    def regenerate_invite(self, workplace: Workplace) -> Workplace:
        workplace.invite_key = generate_invite_key()
        workplace.save(update_fields=["invite_key"])

        return workplace

    def join_workplace(self, user: User, invite_key: str) -> WorkplaceMember:
        key = invite_key.strip()
        workplace_member = WorkplaceMemberService()

        workplace = self.get_or_none(
            invite_key=key,
            deleted_at__isnull=True,
            is_active=True,
        )

        if workplace is None:
            raise WorkplaceNotFound

        member, created = workplace_member.get_or_create(
            workplace=workplace,
            user=user,
            defaults={
                "role": WorkplaceMemberRole.DESIGNER,
                "status": WorkplaceMemberStatus.PENDING,
            },
        )

        if created:
            admins = WorkplaceMember.objects.filter(
                workplace=workplace,
                role__in=(WorkplaceMemberRole.OWNER, WorkplaceMemberRole.MANAGER),
                status=WorkplaceMemberStatus.ACTIVE,
            )
            if admins:
                InboxService().send_bulk(
                    members=list(admins),
                    title="Novo pedido de entrada",
                    message=f"{user.email} pediu para entrar no workspace.",
                    type=InboxType.MEMBER_JOIN_REQUESTED,
                )

        return member
