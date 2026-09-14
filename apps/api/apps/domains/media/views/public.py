from django.http import HttpRequest, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.streaming.views import sse_response

from ..models import Media
from ..realtime import media_channel_name, notify_media_comment
from ..serializers import (
    MediaCommentSerializer,
    MediaPublicCommentSerializer,
    MediaPublicFeedbackSerializer,
    MediaPublicSerializer,
)
from ..services import MediaCommentService, MediaFeedbackService

# The public share link (`share_token`) is the whole authorization model here — no
# session, no `x-workplace-id`. Anyone with the link can view/comment/react, same as
# the frontend page it backs (`app/src/pages/public/media/[id].vue`, outside the
# dashboard, no login). Never gate these behind `WorkplaceViewSetMixin`/`IsAuthenticated`.


def _get_media(token) -> Media:
    return get_object_or_404(Media, share_token=token)


@extend_schema(tags=["Media Public"])
class MediaPublicDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: HttpRequest, token):
        media = _get_media(token)

        return Response(MediaPublicSerializer(media).data)


@extend_schema(tags=["Media Public"])
class MediaPublicCommentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: HttpRequest, token):
        media = _get_media(token)

        serializer = MediaPublicCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        version = data.get("version")

        if version and version.media_id != media.id:
            return Response(
                {"version": ["Versão não pertence a esta mídia."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comment = MediaCommentService().add_comment(
            media_id=media.id,
            version_id=version.id if version else None,
            content=data["content"],
            guest_name=data["guest_name"],
        )

        notify_media_comment(comment)

        return Response(MediaCommentSerializer(comment).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Media Public"])
class MediaPublicFeedbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: HttpRequest, token):
        media = _get_media(token)

        serializer = MediaPublicFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        version = data.get("version")

        if version and version.media_id != media.id:
            return Response(
                {"version": ["Versão não pertence a esta mídia."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        MediaFeedbackService().add_feedback(
            media_id=media.id,
            user_id=None,
            version_id=version.id if version else None,
            decision=data.get("decision"),
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


async def media_public_sse(request: HttpRequest, token):
    """Same channel as the authenticated `MediaViewSet.sse` action
    (`media_channel_name`) — a comment from either side reaches everyone watching,
    dashboard or public link."""
    media = await Media.objects.filter(share_token=token).values("id").afirst()

    if media is None:
        return HttpResponseNotFound()

    return sse_response(media_channel_name(media["id"]))
