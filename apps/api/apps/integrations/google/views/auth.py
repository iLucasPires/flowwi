"""Google OAuth2 connection views."""

import logging

from django.conf import settings
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.domains.workplace.mixins import WorkplaceViewSetMixin

from ..models import GoogleDriveConnection
from ..serializers import GoogleDriveConnectionSerializer
from ..services.google import GoogleDriveService

logger = logging.getLogger(__name__)


@extend_schema(tags=["Google Auth"])
class GoogleAuthViewSet(WorkplaceViewSetMixin, viewsets.ModelViewSet):
    queryset = GoogleDriveConnection.objects.all()
    serializer_class = GoogleDriveConnectionSerializer
    permission_classes = [IsAuthenticated]

    UNAUTHENTICATED_ACTIONS = ("callback",)

    def get_permissions(self):
        if self.action in self.UNAUTHENTICATED_ACTIONS:
            return [AllowAny()]

        return super().get_permissions()

    def get_authenticators(self):
        if getattr(self, "action", None) in self.UNAUTHENTICATED_ACTIONS:
            return []

        return super().get_authenticators()

    # ── OAuth Flow ────────────────────────────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="auth-url")
    def auth_url(self, request):
        workplace = self.get_workplace()
        service = GoogleDriveService()

        state = service.generate_state(str(workplace.id), request.user.id)

        url = service.get_auth_url(request, state=state)

        return Response({"url": url, "state": state})

    @action(detail=False, methods=["get"], url_path="callback")
    def callback(self, request):
        error = request.query_params.get("error")
        if error:
            return self._callback_response(request, success=False)

        code = request.query_params.get("code")
        state = request.query_params.get("state")

        if not code or not state:
            return self._callback_response(request, success=False)

        service = GoogleDriveService()
        state_data = service.verify_state(state)

        if not state_data:
            return self._callback_response(request, success=False)

        workplace_id, user_id = state_data

        try:
            tokens = service.exchange_code(code, request, state)
        except Exception:
            logger.exception("Token exchange failed")
            return self._callback_response(request, success=False)

        GoogleDriveConnection.objects.update_or_create(
            workplace_id=workplace_id,
            connected_by_id=user_id,
            defaults={
                "access_token": tokens["access_token"],
                "refresh_token": tokens.get("refresh_token", ""),
                "token_expires_at": tokens.get("expires_at"),
                "is_active": True,
            },
        )

        service.mark_state_completed(state)
        return self._callback_response(request, success=True)

    @action(detail=False, methods=["get"], url_path="auth-status")
    def auth_status(self, request):
        state = request.query_params.get("state")
        if not state:
            return Response({"completed": False})

        service = GoogleDriveService()

        return Response({"completed": service.is_state_completed(state)})

    @action(detail=True, methods=["post"], url_path="disconnect")
    def disconnect(self, request, pk=None):
        connection = self.get_object()
        connection.is_active = False
        connection.save(update_fields=["is_active"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _callback_response(self, request, *, success: bool):
        response = render(
            request,
            template_name="google/oauth_callback.html",
            context={
                "success": success,
                "frontend_origin": settings.FRONTEND_URL,
            },
        )

        for header, value in {
            "Content-Security-Policy": "default-src 'none'; script-src 'unsafe-inline'",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer",
            "Cache-Control": "no-store",
        }.items():
            response[header] = value

        return response
