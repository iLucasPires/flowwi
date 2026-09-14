from .comment import DocumentCommentViewSet
from .document import DocumentViewSet
from .feedback import DocumentFeedbackViewSet
from .type import DocumentTypeViewSet
from .version import DocumentVersionViewSet

__all__ = [
    "DocumentCommentViewSet",
    "DocumentFeedbackViewSet",
    "DocumentTypeViewSet",
    "DocumentVersionViewSet",
    "DocumentViewSet",
]
