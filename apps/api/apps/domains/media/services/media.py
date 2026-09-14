from lib.bases import ServiceBase

from ..models import Media


class MediaService(ServiceBase):
    def __init__(self):
        super().__init__(model=Media)
