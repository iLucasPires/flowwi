import json
from typing import override

from rest_framework.renderers import BaseRenderer

from lib.enums import MimeType


class SSERenderer(BaseRenderer):
    """
    Formats one event dict (`{"id": str, "event": str, "data": Any}`) as a single
    Server-Sent Events frame.

    Used directly by streaming views, not through DRF's normal response pipeline —
    there's no single `Response` to render, frames are produced one at a time as
    events arrive and yielded into a `StreamingHttpResponse`. `render` stays `async`
    so it can be awaited from that async generator without blocking the event loop.
    """

    format = "event-stream"
    media_type = MimeType.SSE

    @override
    async def render(
        self,
        data,
        accepted_media_type=None,
        renderer_context=None,
    ) -> bytes:
        lines = []

        if data.get("id") is not None:
            lines.append(f"id: {data['id']}")

        if data.get("event"):
            lines.append(f"event: {data['event']}")

        lines.append(f"data: {json.dumps(data.get('data'))}")
        lines.append("")
        lines.append("")

        return "\n".join(lines).encode("utf-8")
