"""
Thin wrapper for publishing Server-Sent Events from regular sync Django code —
views, signals, services. Mirrors `apps.document.realtime`'s channel-layer
helper, but for the SSE side: a plain Redis `PUBLISH`, independent of Django
Channels and of `apps.common.realtime`'s WebSocket dispatcher — the two transports don't
share an event bus, each domain picks the one it needs.

Channel naming mirrors the WS side's per-user group (`user-<id>`, see
`apps.common.realtime.consumers.GlobalConsumer`) so the same identity is reused across
both transports, prefixed with `stream:` to namespace the SSE pub/sub channels
from anything else on the same Redis instance.

Best-effort, no replay: `PUBLISH` only reaches subscribers connected at that exact
moment — there's no backlog, so a client that's mid-reconnect when this fires never
sees that event over the stream (the `id:` field on the SSE frame is informational,
nothing here reads a client's `Last-Event-ID` to backfill). Same philosophy as the
document WS side (see `apps.document.realtime`): treat what you push here
as a "something happened, go refetch if you care" nudge, not as the source of
truth. Only publish events whose underlying state is durable elsewhere (a DB row,
same as `Inbox` here) — if a channel is the only place an event exists, a missed
`PUBLISH` means it's gone for good.
"""

import json
import uuid

from lib.clients import redis_client
from lib.utils import channel_name


def _channel_key(channel: str) -> str:
    return f"stream:{channel}"


def publish_event(channel: str, event: str, data: dict) -> None:
    envelope = {"id": str(uuid.uuid4()), "event": event, "data": data}

    redis_client.publish(_channel_key(channel), json.dumps(envelope))


def publish_to_user(user_id, event: str, data: dict) -> None:
    """Convenience for the common case — push to everything that user has open,
    same identity as the WS `user-<id>` group."""
    publish_event(channel_name("user", user_id), event, data)


def publish_resource_changed(workplace_id, resource: str, action: str, object_id) -> None:
    """Nudge every member of a workplace that a Task/Document/Sticky changed, so their
    lists can sync live across tabs/users — same shape as `apps.inbox.signals`, just
    fanned out to everyone in the workplace instead of one recipient, over each
    member's own `user-<id>` channel (the existing generic `GET /stream` endpoint)
    rather than a new per-workplace channel/endpoint.

    Payload is deliberately just `{id, action, workplace_id}`, never the object itself:
    visibility on these resources is per-viewer (private vs. workplace), so
    broadcasting content here would leak it to members who can't actually see it. The
    client refetches through the normal permission-scoped endpoint instead of trusting
    pushed data — `workplace_id` only lets it skip refetching when the change is for a
    workplace other than the one currently open."""
    from apps.domains.workplace.models import WorkplaceMember

    event = f"{resource}.changed"
    data = {"id": str(object_id), "action": action, "workplace_id": str(workplace_id)}

    member_user_ids = WorkplaceMember.objects.filter(workplace_id=workplace_id).values_list(
        "user_id", flat=True
    )

    for user_id in member_user_ids:
        publish_to_user(user_id, event, data)
