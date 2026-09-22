from django.contrib.auth import get_user_model
from django.utils import timezone

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

    def trash(self, workplace: Workplace) -> Workplace:
        """Soft-delete only — related tasks/documents/stickies/etc. are left as-is.
        There's a lot of data hanging off a workspace to actually purge; that's a
        manual (or later, scheduled) cleanup job, not something that happens here."""
        workplace.deleted_at = timezone.now()
        workplace.save(update_fields=["deleted_at"])

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
                full_name = getattr(getattr(user, "profile", None), "full_name", None)
                requester = f"{full_name} ({user.email})" if full_name else user.email

                InboxService().send_bulk(
                    members=list(admins),
                    title="Novo pedido de entrada",
                    message=(
                        f"{requester} pediu para entrar no workspace {workplace.name}. "
                        "Aprove ou recuse abaixo, ou em Configurações > Membros."
                    ),
                    type=InboxType.MEMBER_JOIN_REQUESTED,
                    related_member=member,
                )

        return member
