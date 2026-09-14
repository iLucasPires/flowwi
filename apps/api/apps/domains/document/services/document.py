from lib.bases import ServiceBase

from ..models import Document


class DocumentService(ServiceBase):
    def __init__(self):
        super().__init__(model=Document)
