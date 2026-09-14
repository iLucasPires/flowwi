from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.domains.inbox.models import InboxType
from apps.domains.inbox.services import InboxService
from apps.domains.workplace.mixins import WorkplaceViewSetMixin
from apps.domains.workplace.models import WorkplaceMember

from ..models import MediaComment
from ..realtime import notify_media_comment
from ..serializers import MediaCommentSerializer


@extend_schema(tags=["Media Comments"])
class MediaCommentViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = MediaComment.objects.all()
    serializer_class = MediaCommentSerializer
    permission_classes = [IsAuthenticated]
    workplace_lookup_field = "media__workplace"

    def get_queryset(self):
        workplace = self.get_workplace()
        if workplace is None:
            return self.queryset.none()
        return self.queryset.filter(**{self.workplace_lookup_field: workplace})

    def perform_create(self, serializer):
        media = serializer.validated_data["media"]
        if media.workplace_id != self.get_workplace().id:
            raise PermissionDenied("Media does not belong to this workplace.")

        comment = serializer.save(author=self.request.user)
        media = comment.media

        notify_media_comment(comment)

        if media.designer_id and media.designer_id != self.request.user.id and media.workplace_id:
            recipient = WorkplaceMember.objects.filter(
                workplace_id=media.workplace_id, user_id=media.designer_id
            ).first()
            sender = WorkplaceMember.objects.filter(workplace_id=media.workplace_id, user=self.request.user).first()

            if recipient:
                InboxService().send_inbox(
                    member=recipient,
                    sender=sender,
                    title=f"Novo comentário em {media.title or 'mídia'}",
                    message=comment.content,
                    type=InboxType.MEDIA_COMMENT,
                )
