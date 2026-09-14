from rest_framework.routers import SimpleRouter

from .views import (
    DocumentCommentViewSet,
    DocumentFeedbackViewSet,
    DocumentTypeViewSet,
    DocumentVersionViewSet,
    DocumentViewSet,
)

router = SimpleRouter(trailing_slash=False)

router.register(r"documents", DocumentViewSet)
router.register(r"document-versions", DocumentVersionViewSet)
router.register(r"document-comments", DocumentCommentViewSet)
router.register(r"document-feedbacks", DocumentFeedbackViewSet)
router.register(r"document-types", DocumentTypeViewSet)

urlpatterns = router.urls
