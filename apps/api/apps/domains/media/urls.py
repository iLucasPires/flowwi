from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (
    MediaCommentViewSet,
    MediaFeedbackViewSet,
    MediaPublicCommentView,
    MediaPublicDetailView,
    MediaPublicFeedbackView,
    MediaVersionViewSet,
    MediaViewSet,
    media_public_sse,
)

router = SimpleRouter(trailing_slash=False)

router.register(r"medias", MediaViewSet)
router.register(r"media-versions", MediaVersionViewSet)
router.register(r"media-comments", MediaCommentViewSet)
router.register(r"media-feedbacks", MediaFeedbackViewSet)

# Public share link (no auth, scoped by `share_token`) — plain paths, not routed through
# `MediaViewSet`: these aren't workplace resources, `WorkplaceViewSetMixin` doesn't apply.
urlpatterns = [
    path("medias/public/<uuid:token>", MediaPublicDetailView.as_view()),
    path("medias/public/<uuid:token>/comment", MediaPublicCommentView.as_view()),
    path("medias/public/<uuid:token>/feedback", MediaPublicFeedbackView.as_view()),
    path("medias/public/<uuid:token>/sse", media_public_sse),
    *router.urls,
]
