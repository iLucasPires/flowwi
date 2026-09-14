"""
Thin wrapper for pushing to a media's SSE channel from regular sync Django code —
views, services. Mirrors `apps.document.realtime`'s channel-layer helper,
but for the SSE side (see `apps.common.streaming`) — unlike document's WS group, this
carries the actual comment in the payload, not just a "go refetch" ping: there's
no `can_edit`/`can_manage_sharing`-style per-viewer permission on a comment, so
broadcasting the same snapshot to everyone watching (dashboard or public share
link) is safe and saves every client a round trip.
"""

from apps.common.streaming.publisher import publish_event
from lib.utils import channel_name

from .models import MediaComment
from .serializers import MediaCommentSerializer


def media_channel_name(media_id) -> str:
    return channel_name("media", media_id)


def notify_media_comment(comment: MediaComment) -> None:
    publish_event(
        media_channel_name(comment.media_id),
        event="media-comment",
        data=MediaCommentSerializer(comment).data,
    )
