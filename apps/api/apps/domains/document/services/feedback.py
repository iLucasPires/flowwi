from lib.bases import ServiceBase

from ..models import DocumentFeedback


class DocumentFeedbackService(ServiceBase):
    def __init__(self):
        super().__init__(model=DocumentFeedback)
