from enum import StrEnum


class MimeType(StrEnum):
    SSE = "text/event-stream"
    PNG = "image/png"
    JPEG = "image/jpeg"
    MP4 = "video/mp4"
    MP3 = "audio/mpeg"
    XML = "application/xml"
    JSON = "application/json"
    PDF = "application/pdf"
