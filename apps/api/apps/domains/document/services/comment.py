from lib.bases import ServiceBase

from ..models import DocumentComment


class DocumentCommentService(ServiceBase):
    def __init__(self):
        super().__init__(model=DocumentComment)
