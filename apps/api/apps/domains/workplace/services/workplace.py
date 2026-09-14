from django.contrib.auth import get_user_model

from apps.domains.inbox.models import InboxType
from apps.domains.inbox.services import InboxService
from lib.bases import ServiceBase

from ..exceptions import WorkplaceNotFound
from ..models import Workplace, WorkplaceMember, WorkplaceMemberRole
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

    def join_workplace(self, user: User, invite_key: str) -> Workplace:
        key = invite_key.strip()
        workplace_member = WorkplaceMemberService()

        workplace = self.get_or_none(
            invite_key=key,
            deleted_at__isnull=True,
            is_active=True,
        )

        if workplace is None:
            raise WorkplaceNotFound

        _member, created = workplace_member.get_or_create(
            workplace=workplace,
            user=user,
            defaults={"role": WorkplaceMemberRole.DESIGNER},
        )

        if created:
            others = WorkplaceMember.objects.filter(workplace=workplace).exclude(user=user)
            if others:
                InboxService().send_bulk(
                    members=list(others),
                    title="Novo membro no workspace",
                    message=f"{user.email} entrou no workspace.",
                    type=InboxType.MEMBER_JOINED,
                )

        return workplace
