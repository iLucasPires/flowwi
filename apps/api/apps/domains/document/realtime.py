"""
Thin wrapper around the channel layer for pushing to a document's WebSocket group
from regular sync Django code — views, signals, services. Every connection subscribed
to that document (via `apps.common.realtime.consumers.GlobalConsumer` → `DocumentRealtimeHandler`,
over the single `/ws/` connection) is in this group regardless of which browser
tab/user it is — see the api AGENTS.md → Realtime.

Only one kind of event goes out this way: a fire-and-forget "something about this
document changed, go refetch it" ping (type `document.changed`). Deliberately carries
no payload beyond the id — `can_edit`/`can_manage_sharing` are computed per viewer
(author/admin overrides), so broadcasting one snapshot to the whole group would be
wrong for everyone but the user who triggered the change. Cheaper to have each client
re-GET the document than to duplicate that permission logic over the wire.

The edit-lock's own broadcasts (`document.lock_state`) are sent directly by
`DocumentRealtimeHandler` — already async there, so they don't need this sync-side helper.
"""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .services import DocumentRealtimeService


def notify_document_changed(document_id) -> None:
    """Call after any save that affects what a viewer sees: sharing, title, content,
    version status, cover, etc."""
    channel_layer = get_channel_layer()

    if channel_layer is None:
        return

    group_name = DocumentRealtimeService().group_name(document_id)

    async_to_sync(channel_layer.group_send)(
        group_name,
        {"type": "document.changed", "document_id": str(document_id)},
    )
