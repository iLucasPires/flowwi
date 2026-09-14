from typing import override

from rest_framework.renderers import BaseRenderer

from lib.enums import MimeType


class XMLRenderer(BaseRenderer):
    format = "xml"
    media_type = MimeType.XML

    @override
    def render(
        self,
        data,
        accepted_media_type=None,
        renderer_context=None,
    ):
        if data is None:
            return b""

        return data.encode("utf-8")
